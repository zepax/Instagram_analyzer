"""Professional PDF exporter for Instagram analysis reports."""

import io
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, KeepTogether
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.lib.colors import HexColor

from .. import __version__
from ..models import Post, Story, Reel, Profile
from ..utils import anonymize_data


class PDFExporter:
    """Export Instagram analysis to professional PDF reports."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the PDF."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1DA1F2'),
            alignment=1  # Center
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#333333'),
            borderWidth=0,
            borderColor=colors.HexColor('#1DA1F2'),
            borderPadding=5
        ))
        
        # Stat style
        self.styles.add(ParagraphStyle(
            name='StatStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceBefore=6,
            spaceAfter=6,
            leftIndent=20
        ))
        
        # Highlight style
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=11,
            backColor=colors.HexColor('#F0F8FF'),
            borderWidth=1,
            borderColor=colors.HexColor('#1DA1F2'),
            borderPadding=8,
            spaceBefore=10,
            spaceAfter=10
        ))
    
    def export(self, analyzer, output_path: Path, anonymize: bool = False) -> Path:
        """Export analysis to PDF report.
        
        Args:
            analyzer: InstagramAnalyzer instance with loaded data
            output_path: Directory to save the report
            anonymize: Whether to anonymize sensitive data
            
        Returns:
            Path to the generated PDF file
        """
        # Generate analysis data
        report_data = self._generate_report_data(analyzer, anonymize)
        
        # Create PDF
        pdf_file = output_path / "instagram_analysis.pdf"
        doc = SimpleDocTemplate(
            str(pdf_file),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build PDF content
        story = self._build_pdf_content(report_data)
        
        # Generate PDF
        doc.build(story)
        
        return pdf_file
    
    def _generate_report_data(self, analyzer, anonymize: bool) -> Dict[str, Any]:
        """Generate comprehensive report data."""
        # Run analysis
        analysis_results = analyzer.analyze()
        
        data = {
            'metadata': self._get_metadata(analyzer, anonymize),
            'overview': self._get_overview_stats(analyzer),
            'temporal_analysis': self._get_temporal_analysis(analyzer),
            'engagement_analysis': self._get_engagement_analysis(analyzer),
            'content_analysis': self._get_content_analysis(analyzer),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if anonymize:
            data = anonymize_data(data)
        
        return data
    
    def _get_metadata(self, analyzer, anonymize: bool) -> Dict[str, Any]:
        """Get report metadata."""
        metadata = {
            'username': (
                'Anonymous User' if anonymize and analyzer.profile else (
                    'No profile data available' if not analyzer.profile else analyzer.profile.username
                )
            ),
            'display_name': (
                'Anonymous' if anonymize and analyzer.profile else (
                    'No profile data available' if not analyzer.profile else analyzer.profile.name
                )
            ),
            'total_posts': len(analyzer.posts),
            'total_stories': len(analyzer.stories),
            'total_reels': len(analyzer.reels),
            'analysis_period': self._get_date_range(analyzer),
            'analyzer_version': __version__,
        }
        return metadata
    
    def _get_overview_stats(self, analyzer) -> Dict[str, Any]:
        """Get overview statistics."""
        total_likes = sum(post.likes_count for post in analyzer.posts if post.likes_count)
        total_comments = sum(post.comments_count for post in analyzer.posts if post.comments_count)
        
        return {
            'total_content': len(analyzer.posts) + len(analyzer.stories) + len(analyzer.reels),
            'total_likes': total_likes,
            'total_comments': total_comments,
            'avg_likes_per_post': round(total_likes / len(analyzer.posts), 1) if analyzer.posts else 0,
            'avg_comments_per_post': round(total_comments / len(analyzer.posts), 1) if analyzer.posts else 0,
            'engagement_rate': self._calculate_engagement_rate(analyzer)
        }
    
    def _get_temporal_analysis(self, analyzer) -> Dict[str, Any]:
        """Get temporal analysis data."""
        if not analyzer.posts:
            return {}
        
        # Group posts by month
        monthly_posts = Counter()
        for post in analyzer.posts:
            month_key = post.timestamp.strftime('%Y-%m')
            monthly_posts[month_key] += 1
        
        # Group by day of week
        weekday_posts = Counter()
        for post in analyzer.posts:
            weekday_posts[post.timestamp.strftime('%A')] += 1
        
        return {
            'monthly_distribution': dict(monthly_posts.most_common()),
            'weekday_distribution': dict(weekday_posts.most_common()),
            'most_active_month': monthly_posts.most_common(1)[0] if monthly_posts else ('N/A', 0),
            'most_active_weekday': weekday_posts.most_common(1)[0] if weekday_posts else ('N/A', 0)
        }
    
    def _get_engagement_analysis(self, analyzer) -> Dict[str, Any]:
        """Get engagement analysis."""
        if not analyzer.posts:
            return {}
        
        posts_with_engagement = [p for p in analyzer.posts if p.likes_count or p.comments_count]
        
        if not posts_with_engagement:
            return {}
        
        # Sort by engagement
        top_posts = sorted(
            posts_with_engagement,
            key=lambda p: (p.likes_count or 0) + (p.comments_count or 0),
            reverse=True
        )[:5]
        
        return {
            'top_posts': [{
                'caption': post.caption[:100] + '...' if post.caption and len(post.caption) > 100 else post.caption or 'No caption',
                'likes': post.likes_count or 0,
                'comments': post.comments_count or 0,
                'total_engagement': (post.likes_count or 0) + (post.comments_count or 0)
            } for post in top_posts],
            'avg_engagement': round(
                sum((p.likes_count or 0) + (p.comments_count or 0) for p in posts_with_engagement) / len(posts_with_engagement), 1
            )
        }
    
    def _get_content_analysis(self, analyzer) -> Dict[str, Any]:
        """Get content analysis."""
        # Analyze media types
        media_types = Counter()
        for post in analyzer.posts:
            if hasattr(post, 'media') and post.media:
                for media in post.media:
                    media_types[media.media_type] += 1
            else:
                media_types['unknown'] += 1
        
        # Analyze hashtags
        all_hashtags = []
        for post in analyzer.posts:
            if post.caption:
                hashtags = [word for word in post.caption.split() if word.startswith('#')]
                all_hashtags.extend(hashtags)
        
        hashtag_counts = Counter(all_hashtags)
        
        return {
            'media_types': dict(media_types.most_common()),
            'top_hashtags': dict(hashtag_counts.most_common(10)),
            'total_hashtags': len(all_hashtags),
            'unique_hashtags': len(hashtag_counts)
        }
    
    def _get_date_range(self, analyzer) -> str:
        """Get the date range of the data."""
        all_dates = []
        for post in analyzer.posts:
            all_dates.append(post.timestamp)
        for story in analyzer.stories:
            all_dates.append(story.timestamp)
        for reel in analyzer.reels:
            all_dates.append(reel.timestamp)
        
        if not all_dates:
            return 'No data available'
        
        min_date = min(all_dates)
        max_date = max(all_dates)
        return f"{min_date.strftime('%B %Y')} - {max_date.strftime('%B %Y')}"
    
    def _calculate_engagement_rate(self, analyzer) -> float:
        """Calculate overall engagement rate."""
        if not analyzer.posts:
            return 0.0
        
        total_engagement = sum(
            (post.likes_count or 0) + (post.comments_count or 0)
            for post in analyzer.posts
        )
        
        return round(total_engagement / len(analyzer.posts), 2)
    
    def _build_pdf_content(self, data: Dict[str, Any]) -> List[Any]:
        """Build the PDF content structure."""
        story = []
        
        # Title page
        story.extend(self._create_title_page(data))
        story.append(PageBreak())
        
        # Overview section
        story.extend(self._create_overview_section(data))
        story.append(Spacer(1, 20))
        
        # Temporal analysis section
        story.extend(self._create_temporal_section(data))
        story.append(Spacer(1, 20))
        
        # Engagement analysis section
        story.extend(self._create_engagement_section(data))
        story.append(Spacer(1, 20))
        
        # Content analysis section
        story.extend(self._create_content_section(data))
        
        return story
    
    def _create_title_page(self, data: Dict[str, Any]) -> List[Any]:
        """Create the title page."""
        content = []
        
        # Main title
        content.append(Spacer(1, 100))
        content.append(Paragraph("Instagram Analysis Report", self.styles['CustomTitle']))
        content.append(Spacer(1, 30))
        
        # User info
        metadata = data['metadata']
        content.append(Paragraph(f"<b>Account:</b> {metadata['username']}", self.styles['Normal']))
        content.append(Paragraph(f"<b>Display Name:</b> {metadata['display_name']}", self.styles['Normal']))
        content.append(Paragraph(f"<b>Analysis Period:</b> {metadata['analysis_period']}", self.styles['Normal']))
        content.append(Spacer(1, 20))
        
        # Summary stats
        content.append(Paragraph(f"<b>Total Posts:</b> {metadata['total_posts']}", self.styles['Normal']))
        content.append(Paragraph(f"<b>Total Stories:</b> {metadata['total_stories']}", self.styles['Normal']))
        content.append(Paragraph(f"<b>Total Reels:</b> {metadata['total_reels']}", self.styles['Normal']))
        content.append(Spacer(1, 50))
        
        # Generation info
        content.append(Paragraph(f"<i>Generated on {data['generated_at']}</i>", self.styles['Normal']))
        
        return content
    
    def _create_overview_section(self, data: Dict[str, Any]) -> List[Any]:
        """Create overview section."""
        content = []
        overview = data.get('overview', {})
        
        content.append(Paragraph("📊 Content Overview", self.styles['SectionHeader']))
        
        # Create overview table
        overview_data = [
            ['Metric', 'Value'],
            ['Total Content Items', str(overview.get('total_content', 0))],
            ['Total Likes', f"{overview.get('total_likes', 0):,}"],
            ['Total Comments', f"{overview.get('total_comments', 0):,}"],
            ['Avg Likes per Post', str(overview.get('avg_likes_per_post', 0))],
            ['Avg Comments per Post', str(overview.get('avg_comments_per_post', 0))],
            ['Engagement Rate', f"{overview.get('engagement_rate', 0):.1f}"]
        ]
        
        table = Table(overview_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1DA1F2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        content.append(table)
        return content
    
    def _create_temporal_section(self, data: Dict[str, Any]) -> List[Any]:
        """Create temporal analysis section."""
        content = []
        temporal = data.get('temporal_analysis', {})
        
        content.append(Paragraph("📅 Temporal Patterns", self.styles['SectionHeader']))
        
        if temporal:
            most_active_month = temporal.get('most_active_month', ('N/A', 0))
            most_active_weekday = temporal.get('most_active_weekday', ('N/A', 0))
            
            content.append(Paragraph(
                f"<b>Most Active Month:</b> {most_active_month[0]} ({most_active_month[1]} posts)",
                self.styles['StatStyle']
            ))
            content.append(Paragraph(
                f"<b>Most Active Day:</b> {most_active_weekday[0]} ({most_active_weekday[1]} posts)",
                self.styles['StatStyle']
            ))
            
            # Monthly distribution table
            monthly_dist = temporal.get('monthly_distribution', {})
            if monthly_dist:
                content.append(Spacer(1, 10))
                content.append(Paragraph("<b>Monthly Distribution:</b>", self.styles['Normal']))
                
                month_data = [['Month', 'Posts']]
                for month, count in list(monthly_dist.items())[:12]:  # Show top 12 months
                    month_data.append([month, str(count)])
                
                if len(month_data) > 1:
                    month_table = Table(month_data, colWidths=[2*inch, 1*inch])
                    month_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1DA1F2')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    content.append(month_table)
        else:
            content.append(Paragraph("No temporal data available.", self.styles['Normal']))
        
        return content
    
    def _create_engagement_section(self, data: Dict[str, Any]) -> List[Any]:
        """Create engagement analysis section."""
        content = []
        engagement = data.get('engagement_analysis', {})
        
        content.append(Paragraph("💝 Engagement Analysis", self.styles['SectionHeader']))
        
        if engagement and engagement.get('top_posts'):
            content.append(Paragraph(
                f"<b>Average Engagement per Post:</b> {engagement.get('avg_engagement', 0)} interactions",
                self.styles['StatStyle']
            ))
            content.append(Spacer(1, 10))
            content.append(Paragraph("<b>Top Performing Posts:</b>", self.styles['Normal']))
            
            # Top posts table
            posts_data = [['Caption', 'Likes', 'Comments', 'Total']]
            for post in engagement['top_posts']:
                caption = post['caption'][:50] + '...' if len(post['caption']) > 50 else post['caption']
                posts_data.append([
                    caption,
                    str(post['likes']),
                    str(post['comments']),
                    str(post['total_engagement'])
                ])
            
            posts_table = Table(posts_data, colWidths=[3*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            posts_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1DA1F2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            content.append(posts_table)
        else:
            content.append(Paragraph("No engagement data available.", self.styles['Normal']))
        
        return content
    
    def _create_content_section(self, data: Dict[str, Any]) -> List[Any]:
        """Create content analysis section."""
        content = []
        content_analysis = data.get('content_analysis', {})
        
        content.append(Paragraph("📱 Content Analysis", self.styles['SectionHeader']))
        
        if content_analysis:
            # Media types
            media_types = content_analysis.get('media_types', {})
            if media_types:
                content.append(Paragraph("<b>Media Types Distribution:</b>", self.styles['Normal']))
                for media_type, count in media_types.items():
                    content.append(Paragraph(f"• {media_type.title()}: {count}", self.styles['StatStyle']))
                content.append(Spacer(1, 10))
            
            # Hashtags analysis
            total_hashtags = content_analysis.get('total_hashtags', 0)
            unique_hashtags = content_analysis.get('unique_hashtags', 0)
            
            content.append(Paragraph(f"<b>Hashtag Usage:</b>", self.styles['Normal']))
            content.append(Paragraph(f"• Total hashtags used: {total_hashtags}", self.styles['StatStyle']))
            content.append(Paragraph(f"• Unique hashtags: {unique_hashtags}", self.styles['StatStyle']))
            
            # Top hashtags
            top_hashtags = content_analysis.get('top_hashtags', {})
            if top_hashtags:
                content.append(Spacer(1, 10))
                content.append(Paragraph("<b>Most Used Hashtags:</b>", self.styles['Normal']))
                
                hashtag_data = [['Hashtag', 'Usage Count']]
                for hashtag, count in list(top_hashtags.items())[:10]:
                    hashtag_data.append([hashtag, str(count)])
                
                if len(hashtag_data) > 1:
                    hashtag_table = Table(hashtag_data, colWidths=[2.5*inch, 1*inch])
                    hashtag_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1DA1F2')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    content.append(hashtag_table)
        else:
            content.append(Paragraph("No content analysis data available.", self.styles['Normal']))
        
        return content