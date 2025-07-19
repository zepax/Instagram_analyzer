"""
FastAPI Web Dashboard for Personal Instagram Analysis

Simple web interface for individual users to analyze their Instagram exports.
Designed for hobbyists and personal use.
"""

import asyncio
import logging
import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from zipfile import ZipFile

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.requests import Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from instagram_analyzer.core.analyzer import InstagramAnalyzer
from instagram_analyzer.mcp.filesystem import MCPFileSystemError, get_mcp_filesystem
from instagram_analyzer.mcp.redis_adapter import MCPRedisError, get_mcp_redis
from instagram_analyzer.utils.file_utils import safe_json_load

# Get the package directory
package_dir = Path(__file__).parent.parent
static_dir = package_dir / "static"
templates_dir = package_dir / "templates"

# FastAPI App
app = FastAPI(
    title="Instagram Personal Analyzer",
    description="Personal web dashboard for Instagram data analysis",
    version="0.2.08",
)

# Static files and templates
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

# MCP-enhanced storage
mcp_filesystem = get_mcp_filesystem()
mcp_redis = get_mcp_redis()

# Fallback in-memory job storage (when Redis not available)
analysis_jobs: Dict[str, Dict[str, Any]] = {}

# Logger
logger = logging.getLogger(__name__)


class AnalysisJob(BaseModel):
    """Analysis job model"""

    job_id: str
    status: str  # "uploading", "processing", "completed", "error"
    progress: int  # 0-100
    message: str
    result_path: Optional[str] = None
    error_message: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.post("/api/upload")
async def upload_instagram_export(
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
):
    """Upload Instagram export ZIP file for analysis with MCP enhancement"""

    try:
        # Basic file validation
        if not file.filename.endswith(".zip"):
            raise HTTPException(status_code=400, detail="Only ZIP files are supported")

        # Generate job ID and session
        job_id = str(uuid.uuid4())
        session_id = await mcp_redis.create_session()

        # Create secure temporary directory using MCP filesystem
        temp_dir = await mcp_filesystem.create_secure_temp_dir(
            f"instagram_analysis_{job_id}_"
        )

        # Save uploaded file
        zip_path = temp_dir / file.filename
        with open(zip_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Enhanced file validation using MCP filesystem
        try:
            validation_result = await mcp_filesystem.validate_upload(zip_path)

            if not validation_result["valid"]:
                await mcp_filesystem.cleanup_temp_directories()
                raise HTTPException(
                    status_code=400,
                    detail=f"File validation failed: {', '.join(validation_result['errors'])}",
                )

        except MCPFileSystemError as e:
            await mcp_filesystem.cleanup_temp_directories()
            raise HTTPException(status_code=400, detail=str(e))

        # Initialize job with MCP Redis
        job_data = {
            "job_id": job_id,
            "session_id": session_id,
            "status": "uploaded",
            "progress": 10,
            "message": "File uploaded and validated successfully",
            "zip_path": str(zip_path),
            "temp_dir": str(temp_dir),
            "file_info": {
                "filename": file.filename,
                "size_mb": validation_result.get("size_mb", 0),
                "file_hash": validation_result.get("file_hash"),
                "security_status": validation_result.get("security_status"),
            },
        }

        # Store job in Redis or fallback
        await mcp_redis.set_progress(job_id, job_data)
        analysis_jobs[job_id] = job_data  # Fallback storage

        # Update session with active job
        await mcp_redis.update_session(session_id, {"active_jobs": [job_id]})

        # Start background analysis
        background_tasks.add_task(process_instagram_analysis_mcp, job_id)

        return {
            "job_id": job_id,
            "session_id": session_id,
            "status": "uploaded",
            "message": "File uploaded, validated and analysis starting...",
            "file_info": job_data["file_info"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/progress/{job_id}")
async def get_analysis_progress(job_id: str):
    """Get real-time analysis progress"""

    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = analysis_jobs[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"],
        "error_message": job.get("error_message"),
    }


@app.get("/api/analysis/{job_id}")
async def get_analysis_results(job_id: str):
    """Get analysis results as JSON"""

    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = analysis_jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed yet")

    # Load analysis results
    try:
        results_path = Path(job["temp_dir"]) / "analysis_results.json"
        results = safe_json_load(str(results_path))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading results: {str(e)}")


@app.get("/api/download/{job_id}")
async def download_html_report(job_id: str):
    """Download generated HTML report"""

    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = analysis_jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed yet")

    html_path = Path(job["temp_dir"]) / "instagram_analysis.html"

    if not html_path.exists():
        raise HTTPException(status_code=404, detail="HTML report not found")

    return FileResponse(
        path=str(html_path),
        filename=f"instagram_analysis_{job_id}.html",
        media_type="text/html",
    )


@app.get("/api/data/overview/{job_id}")
async def get_overview_data(job_id: str):
    """Get basic stats for dashboard cards"""

    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = analysis_jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed yet")

    # Load and return overview data
    try:
        results_path = Path(job["temp_dir"]) / "analysis_results.json"
        results = safe_json_load(str(results_path))

        overview = results.get("basic_stats", {})
        return {
            "total_posts": overview.get("total_posts", 0),
            "total_stories": overview.get("total_stories", 0),
            "total_reels": overview.get("total_reels", 0),
            "total_likes": overview.get("total_likes", 0),
            "total_comments": overview.get("total_comments", 0),
            "date_range": overview.get("date_range", {}),
            "engagement_rate": overview.get("engagement_rate", 0),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading overview: {str(e)}")


async def process_instagram_analysis_mcp(job_id: str):
    """Enhanced background task using MCP capabilities"""

    try:
        # Get job data from Redis or fallback
        job_data = await mcp_redis.get_progress(job_id)
        if not job_data:
            job_data = analysis_jobs.get(job_id)
            if not job_data:
                logger.error(f"Job {job_id} not found")
                return

        zip_path = Path(job_data["zip_path"])
        temp_dir = Path(job_data["temp_dir"])
        extract_dir = temp_dir / "extracted"

        # Check for cached results first
        file_hash = job_data.get("file_info", {}).get("file_hash")
        if file_hash:
            cache_key = await mcp_redis.generate_cache_key(file_hash, "full_analysis")
            cached_results = await mcp_redis.get_cached_analysis(cache_key)

            if cached_results:
                logger.info(f"Using cached results for job {job_id}")

                # Update progress to completed with cached data
                job_data.update(
                    {
                        "status": "completed",
                        "progress": 100,
                        "message": "Analysis completed using cached results!",
                        "cached": True,
                    }
                )

                # Save cached results to file
                results_path = temp_dir / "analysis_results.json"
                import json

                with open(results_path, "w", encoding="utf-8") as f:
                    json.dump(
                        cached_results, f, indent=2, default=str, ensure_ascii=False
                    )

                job_data["result_path"] = str(results_path)

                await mcp_redis.set_progress(job_id, job_data)
                analysis_jobs[job_id] = job_data

                # Publish completion notification
                await mcp_redis.publish_notification(
                    f"job_{job_id}",
                    {
                        "type": "completed",
                        "message": "Analysis completed using cached results",
                    },
                )

                return

        # Update status: starting extraction
        job_data.update(
            {
                "status": "extracting",
                "progress": 20,
                "message": "Extracting ZIP file with enhanced security...",
            }
        )

        await mcp_redis.set_progress(job_id, job_data)
        analysis_jobs[job_id] = job_data

        # Enhanced extraction using MCP filesystem
        extract_dir.mkdir(exist_ok=True)

        async for progress_update in mcp_filesystem.extract_with_progress(
            zip_path, extract_dir
        ):
            if progress_update["status"] == "extracting":
                extraction_progress = 20 + (progress_update["progress"] * 0.2)  # 20-40%
                job_data.update(
                    {
                        "progress": int(extraction_progress),
                        "message": f"Extracting: {progress_update.get('current_file', 'files...')}",
                    }
                )

                await mcp_redis.set_progress(job_id, job_data)
                analysis_jobs[job_id] = job_data

            elif progress_update["status"] == "error":
                raise Exception(f"Extraction failed: {progress_update['error']}")

        # Update status: analyzing
        job_data.update(
            {
                "status": "analyzing",
                "progress": 40,
                "message": "Analyzing Instagram data...",
            }
        )

        await mcp_redis.set_progress(job_id, job_data)
        analysis_jobs[job_id] = job_data

        # Initialize analyzer
        analyzer = InstagramAnalyzer(data_path=str(extract_dir), show_progress=False)

        # Update status: loading data
        job_data.update({"progress": 60, "message": "Loading data..."})

        await mcp_redis.set_progress(job_id, job_data)
        analysis_jobs[job_id] = job_data

        # Load data
        analyzer.load_data()

        # Update status: running analysis
        job_data.update({"progress": 80, "message": "Running comprehensive analysis..."})

        await mcp_redis.set_progress(job_id, job_data)
        analysis_jobs[job_id] = job_data

        # Run analysis
        results = analyzer.analyze()

        # Cache results for future use
        if file_hash:
            await mcp_redis.cache_analysis(
                cache_key, results, ttl=86400
            )  # Cache for 24 hours

        # Save results as JSON
        results_path = temp_dir / "analysis_results.json"
        import json

        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)

        # Update status: generating report
        job_data.update({"progress": 90, "message": "Generating HTML report..."})

        await mcp_redis.set_progress(job_id, job_data)
        analysis_jobs[job_id] = job_data

        # Generate HTML report
        html_path = temp_dir / "instagram_analysis.html"
        analyzer.export_html(str(html_path), compact=True)

        # Complete
        job_data.update(
            {
                "status": "completed",
                "progress": 100,
                "message": "Analysis completed successfully!",
                "result_path": str(results_path),
                "cached": False,
            }
        )

        await mcp_redis.set_progress(job_id, job_data)
        analysis_jobs[job_id] = job_data

        # Publish completion notification
        await mcp_redis.publish_notification(
            f"job_{job_id}",
            {"type": "completed", "message": "Analysis completed successfully"},
        )

        # Update session
        session_id = job_data.get("session_id")
        if session_id:
            session_data = await mcp_redis.get_session(session_id)
            if session_data:
                analysis_history = session_data.get("analysis_history", [])
                analysis_history.append(
                    {
                        "job_id": job_id,
                        "completed_at": datetime.utcnow().isoformat(),
                        "file_info": job_data.get("file_info", {}),
                    }
                )

                await mcp_redis.update_session(
                    session_id, {"analysis_history": analysis_history}
                )

    except Exception as e:
        logger.error(f"Analysis failed for job {job_id}: {e}")

        error_data = {
            "status": "error",
            "progress": 0,
            "message": "Analysis failed",
            "error_message": str(e),
        }

        await mcp_redis.set_progress(job_id, error_data)
        if job_id in analysis_jobs:
            analysis_jobs[job_id].update(error_data)

        # Publish error notification
        await mcp_redis.publish_notification(
            f"job_{job_id}", {"type": "error", "message": f"Analysis failed: {str(e)}"}
        )


# Keep original function for backward compatibility
async def process_instagram_analysis(job_id: str):
    """Legacy background task - delegates to MCP version"""
    await process_instagram_analysis_mcp(job_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)  # nosec
