// Instagram Personal Analyzer - Dashboard JavaScript

// Global variables
let currentJobId = null;
let progressInterval = null;
let charts = {};

// DOM Elements
const uploadSection = document.getElementById('upload-section');
const progressSection = document.getElementById('progress-section');
const resultsSection = document.getElementById('results-section');
const errorSection = document.getElementById('error-section');
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const fileButton = document.getElementById('file-button');
const progressBar = document.getElementById('progress-bar');
const progressMessage = document.getElementById('progress-message');
const progressDetails = document.getElementById('progress-details');
const downloadBtn = document.getElementById('download-btn');

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeUploadArea();
    initializeFileInput();
    resetDashboard();
});

// Upload Area Functionality
function initializeUploadArea() {
    // Drag and drop functionality
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    // Click to browse
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });

    fileButton.addEventListener('click', function(e) {
        e.stopPropagation();
        fileInput.click();
    });
}

function initializeFileInput() {
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

// File Upload Handler
async function handleFileUpload(file) {
    // Validate file
    if (!file.name.endsWith('.zip')) {
        showError('Please select a ZIP file containing your Instagram export.');
        return;
    }

    if (file.size > 500 * 1024 * 1024) { // 500MB limit
        showError('File is too large. Please ensure your export is under 500MB.');
        return;
    }

    // Show progress section
    showProgressSection();

    try {
        // Create form data
        const formData = new FormData();
        formData.append('file', file);

        // Upload file
        updateProgress(10, 'Uploading file...', 'Please wait while we upload your Instagram export');

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }

        const result = await response.json();
        currentJobId = result.job_id;

        // Start progress monitoring
        startProgressMonitoring();

    } catch (error) {
        console.error('Upload error:', error);
        showError(`Upload failed: ${error.message}`);
    }
}

// Progress Monitoring
function startProgressMonitoring() {
    if (progressInterval) {
        clearInterval(progressInterval);
    }

    progressInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/progress/${currentJobId}`);
            if (!response.ok) {
                throw new Error('Failed to get progress');
            }

            const progress = await response.json();
            updateProgress(progress.progress, progress.message, getProgressDetails(progress.status));

            // Check if completed
            if (progress.status === 'completed') {
                clearInterval(progressInterval);
                await loadResults();
            } else if (progress.status === 'error') {
                clearInterval(progressInterval);
                showError(progress.error_message || 'Analysis failed');
            }

        } catch (error) {
            console.error('Progress monitoring error:', error);
            clearInterval(progressInterval);
            showError('Failed to monitor progress');
        }
    }, 2000); // Check every 2 seconds
}

function getProgressDetails(status) {
    const details = {
        'uploaded': 'File uploaded successfully',
        'extracting': 'Extracting ZIP file contents',
        'analyzing': 'Analyzing your Instagram data',
        'processing': 'Processing posts, stories, and interactions',
        'completed': 'Analysis completed successfully!'
    };
    return details[status] || 'Processing...';
}

// Load and Display Results
async function loadResults() {
    try {
        // Load overview data
        const overviewResponse = await fetch(`/api/data/overview/${currentJobId}`);
        if (!overviewResponse.ok) {
            throw new Error('Failed to load overview data');
        }

        const overview = await overviewResponse.json();
        displayOverview(overview);

        // Load full analysis data for charts
        const analysisResponse = await fetch(`/api/analysis/${currentJobId}`);
        if (!analysisResponse.ok) {
            throw new Error('Failed to load analysis data');
        }

        const analysisData = await analysisResponse.json();
        displayCharts(analysisData);
        displayNetworkGraph(analysisData);

        // Setup download button
        setupDownloadButton();

        // Show results section
        showResultsSection();

    } catch (error) {
        console.error('Results loading error:', error);
        showError(`Failed to load results: ${error.message}`);
    }
}

// Display Functions
function displayOverview(data) {
    document.getElementById('total-posts').textContent = formatNumber(data.total_posts);
    document.getElementById('total-stories').textContent = formatNumber(data.total_stories);
    document.getElementById('total-likes').textContent = formatNumber(data.total_likes);
    document.getElementById('total-comments').textContent = formatNumber(data.total_comments);

    // Add animation
    animateNumbers();
}

function displayCharts(data) {
    // Content Distribution Chart
    createContentChart(data);

    // Engagement Chart
    createEngagementChart(data);
}

function createContentChart(data) {
    const ctx = document.getElementById('content-chart').getContext('2d');

    const stats = data.basic_stats || {};
    const chartData = {
        labels: ['Posts', 'Stories', 'Reels'],
        datasets: [{
            data: [
                stats.total_posts || 0,
                stats.total_stories || 0,
                stats.total_reels || 0
            ],
            backgroundColor: [
                '#f09433',
                '#e6683c',
                '#dc2743'
            ],
            borderWidth: 0,
            hoverOffset: 10
        }]
    };

    charts.contentChart = new Chart(ctx, {
        type: 'doughnut',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            },
            cutout: '60%'
        }
    });
}

function createEngagementChart(data) {
    const ctx = document.getElementById('engagement-chart').getContext('2d');

    const stats = data.basic_stats || {};
    const chartData = {
        labels: ['Likes', 'Comments', 'Shares'],
        datasets: [{
            label: 'Engagement',
            data: [
                stats.total_likes || 0,
                stats.total_comments || 0,
                stats.total_shares || 0
            ],
            backgroundColor: 'rgba(240, 148, 51, 0.2)',
            borderColor: '#f09433',
            borderWidth: 2,
            fill: true,
            tension: 0.4
        }]
    };

    charts.engagementChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatNumber(value);
                        }
                    }
                }
            }
        }
    });
}

function displayNetworkGraph(data) {
    // Check if network data exists
    const networkData = data.network_graph || null;

    if (!networkData || !networkData.nodes || networkData.nodes.length === 0) {
        document.getElementById('network-graph').innerHTML =
            '<div class="text-center text-muted p-4">No network data available</div>';
        return;
    }

    // Clear previous graph
    d3.select("#network-graph").selectAll("*").remove();

    // Set up dimensions
    const container = document.getElementById('network-graph');
    const width = container.clientWidth;
    const height = 400;

    // Create SVG
    const svg = d3.select("#network-graph")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    // Create simulation
    const simulation = d3.forceSimulation(networkData.nodes)
        .force("link", d3.forceLink(networkData.links).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-300))
        .force("center", d3.forceCenter(width / 2, height / 2));

    // Create links
    const link = svg.append("g")
        .selectAll("line")
        .data(networkData.links)
        .enter().append("line")
        .attr("class", "link")
        .style("stroke-width", d => Math.sqrt(d.value || 1));

    // Create nodes
    const node = svg.append("g")
        .selectAll("circle")
        .data(networkData.nodes)
        .enter().append("circle")
        .attr("class", "node")
        .attr("r", d => Math.max(5, (d.size || 10)))
        .style("fill", d => d.color || "#f09433")
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended));

    // Add tooltips
    node.append("title")
        .text(d => `${d.name || d.id}\nConnections: ${d.size || 0}`);

    // Update positions
    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("cx", d => d.x)
            .attr("cy", d => d.y);
    });

    // Drag functions
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}

function setupDownloadButton() {
    downloadBtn.addEventListener('click', async function() {
        try {
            const response = await fetch(`/api/download/${currentJobId}`);
            if (!response.ok) {
                throw new Error('Download failed');
            }

            // Create download link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `instagram_analysis_${currentJobId}.html`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

        } catch (error) {
            console.error('Download error:', error);
            showError('Failed to download report');
        }
    });
}

// UI Control Functions
function showProgressSection() {
    uploadSection.style.display = 'none';
    progressSection.style.display = 'block';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';

    progressSection.classList.add('fade-in');
}

function showResultsSection() {
    uploadSection.style.display = 'none';
    progressSection.style.display = 'none';
    resultsSection.style.display = 'block';
    errorSection.style.display = 'none';

    resultsSection.classList.add('slide-up');
}

function showError(message) {
    uploadSection.style.display = 'none';
    progressSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'block';

    document.getElementById('error-message').textContent = message;

    // Clear progress interval
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
}

function resetDashboard() {
    uploadSection.style.display = 'block';
    progressSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';

    currentJobId = null;
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
}

function updateProgress(percentage, message, details) {
    progressBar.style.width = percentage + '%';
    progressBar.textContent = percentage + '%';
    progressMessage.textContent = message;
    progressDetails.textContent = details;
}

// Utility Functions
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function animateNumbers() {
    const numbers = document.querySelectorAll('.h2');
    numbers.forEach(number => {
        const target = parseInt(number.textContent.replace(/[^\d]/g, ''));
        if (target > 0) {
            animateValue(number, 0, target, 1500);
        }
    });
}

function animateValue(element, start, end, duration) {
    const startTime = performance.now();
    const range = end - start;

    function updateValue(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = Math.floor(start + (range * easeOutQuart));

        element.textContent = formatNumber(current);

        if (progress < 1) {
            requestAnimationFrame(updateValue);
        } else {
            element.textContent = formatNumber(end);
        }
    }

    requestAnimationFrame(updateValue);
}
