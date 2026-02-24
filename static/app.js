// API Base URL
const API_BASE_URL = 'http://localhost:8000';

// State management
let forecastsData = {};
let metricsData = {};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkServerConnection();
    // Don't auto-load dashboard, let user click buttons to see results
    // loadDashboard();
});

async function checkServerConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/api`);
        if (response.ok) {
            console.log('Server connection OK');
        }
    } catch (error) {
        showStatus('⚠ Warning: Cannot connect to server. Make sure the FastAPI server is running on port 8000.', 'error');
        console.error('Server connection error:', error);
    }
}

function setupEventListeners() {
    document.getElementById('loadDataBtn').addEventListener('click', loadData);
    document.getElementById('generateEDABtn').addEventListener('click', generateEDA);
    document.getElementById('trainModelsBtn').addEventListener('click', trainModels);
    document.getElementById('generateForecastsBtn').addEventListener('click', generateForecasts);
    document.getElementById('evaluateModelsBtn').addEventListener('click', evaluateModels);
    document.getElementById('refreshBtn').addEventListener('click', loadDashboard);
    document.getElementById('showAllBtn').addEventListener('click', showAllSections);
}

async function showStatus(message, type = 'info') {
    const statusEl = document.getElementById('statusMessage');
    statusEl.textContent = message;
    statusEl.className = `status-message ${type}`;
    setTimeout(() => {
        statusEl.className = 'status-message';
    }, 5000);
}

async function loadData() {
    const btn = document.getElementById('loadDataBtn');
    const originalText = btn.textContent;
    
    try {
        // Disable button and show loading state
        btn.disabled = true;
        btn.textContent = 'Loading...';
        showStatus('Loading and preprocessing data... This may take a moment.', 'info');
        
        // Show all sections initially
        showAllSections();
        
        const response = await fetch(`${API_BASE_URL}/load-data`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showStatus(`✓ Data loaded successfully! Shape: ${data.shape[0]} rows × ${data.shape[1]} columns. Date range: ${data.date_range.start} to ${data.date_range.end}`, 'success');
        } else {
            const errorMsg = data.detail || data.message || 'Unknown error';
            showStatus(`✗ Error: ${errorMsg}`, 'error');
        }
    } catch (error) {
        showStatus(`✗ Error loading data: ${error.message}. Make sure the server is running.`, 'error');
        console.error('Load data error:', error);
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

async function generateEDA() {
    const btn = document.getElementById('generateEDABtn');
    const originalText = btn.textContent;
    
    try {
        btn.disabled = true;
        btn.textContent = 'Generating...';
        showStatus('Generating EDA plots... This may take a moment.', 'info');
        
        // Show only EDA section, hide others
        showOnlySection('eda-section');
        
        const response = await fetch(`${API_BASE_URL}/generate-eda`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showStatus('✓ EDA plots generated successfully! Refreshing plots...', 'success');
            // Hide instruction card
            const edaInstruction = document.getElementById('edaInstruction');
            if (edaInstruction) {
                edaInstruction.style.display = 'none';
            }
            // Wait a bit for files to be written
            setTimeout(() => {
                loadEDAPlots();
            }, 1000);
        } else {
            const errorMsg = data.detail || data.message || 'Unknown error';
            showStatus(`✗ Error: ${errorMsg}`, 'error');
        }
    } catch (error) {
        showStatus(`✗ Error generating EDA: ${error.message}`, 'error');
        console.error('Generate EDA error:', error);
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

async function trainModels() {
    const btn = document.getElementById('trainModelsBtn');
    const originalText = btn.textContent;
    
    try {
        btn.disabled = true;
        btn.textContent = 'Training...';
        showStatus('Training models... This may take 5-10 minutes. Please be patient.', 'info');
        
        // Show all sections
        showAllSections();
        
        const response = await fetch(`${API_BASE_URL}/train-models?model_type=prophet`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showStatus(`✓ Models trained successfully for ${data.junctions.length} junctions!`, 'success');
        } else {
            const errorMsg = data.detail || data.message || 'Unknown error';
            showStatus(`✗ Error: ${errorMsg}`, 'error');
        }
    } catch (error) {
        showStatus(`✗ Error training models: ${error.message}`, 'error');
        console.error('Train models error:', error);
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

async function generateForecasts() {
    const btn = document.getElementById('generateForecastsBtn');
    const originalText = btn.textContent;
    
    try {
        btn.disabled = true;
        btn.textContent = 'Generating...';
        showStatus('Generating forecasts for next 30 days...', 'info');
        
        // Show only forecasts section
        showOnlySection('forecasts-section');
        
        const response = await fetch(`${API_BASE_URL}/generate-forecasts?periods=30`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showStatus('✓ Forecasts generated successfully!', 'success');
            forecastsData = data.forecasts || {};
            displayForecasts();
        } else {
            const errorMsg = data.detail || data.message || 'Unknown error';
            showStatus(`✗ Error: ${errorMsg}`, 'error');
        }
    } catch (error) {
        showStatus(`✗ Error generating forecasts: ${error.message}`, 'error');
        console.error('Generate forecasts error:', error);
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

async function evaluateModels() {
    const btn = document.getElementById('evaluateModelsBtn');
    const originalText = btn.textContent;
    
    try {
        btn.disabled = true;
        btn.textContent = 'Evaluating...';
        showStatus('Evaluating models... Calculating MAE, RMSE, and MAPE metrics.', 'info');
        
        // Show only metrics section
        showOnlySection('metrics-section');
        
        const response = await fetch(`${API_BASE_URL}/evaluate-models?model_type=prophet`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showStatus('✓ Models evaluated successfully!', 'success');
            metricsData = data;
            displayMetrics();
        } else {
            const errorMsg = data.detail || data.message || 'Unknown error';
            showStatus(`✗ Error: ${errorMsg}`, 'error');
        }
    } catch (error) {
        showStatus(`✗ Error evaluating models: ${error.message}`, 'error');
        console.error('Evaluate models error:', error);
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

async function loadDashboard() {
    const btn = document.getElementById('refreshBtn');
    const originalText = btn.textContent;
    
    try {
        btn.disabled = true;
        btn.textContent = 'Refreshing...';
        showStatus('Refreshing dashboard data...', 'info');
        
        // Show all sections when refreshing
        showAllSections();
        
        await Promise.all([
            loadMetrics(),
            loadForecasts(),
            loadEDAPlots()
        ]);
        
        showStatus('✓ Dashboard refreshed!', 'success');
    } catch (error) {
        showStatus(`✗ Error refreshing dashboard: ${error.message}`, 'error');
        console.error('Refresh error:', error);
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

// Function to show only a specific section
function showOnlySection(sectionId) {
    const sections = ['metrics-section', 'forecasts-section', 'eda-section'];
    const welcomeSection = document.getElementById('welcomeSection');
    
    // Hide welcome section when showing results
    if (welcomeSection) {
        welcomeSection.style.display = 'none';
    }
    
    sections.forEach(id => {
        const section = document.querySelector(`.${id}`);
        if (section) {
            if (id === sectionId) {
                section.style.display = 'block';
                // Smooth scroll to the section
                setTimeout(() => {
                    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);
            } else {
                section.style.display = 'none';
            }
        }
    });
}

// Function to show all sections
function showAllSections() {
    const sections = ['metrics-section', 'forecasts-section', 'eda-section'];
    const welcomeSection = document.getElementById('welcomeSection');
    
    // Hide welcome section when showing results
    if (welcomeSection) {
        welcomeSection.style.display = 'none';
    }
    
    sections.forEach(id => {
        const section = document.querySelector(`.${id}`);
        if (section) {
            section.style.display = 'block';
        }
    });
    
    // Scroll to top smoothly
    window.scrollTo({ top: 0, behavior: 'smooth' });
    showStatus('All sections displayed', 'info');
}

async function loadMetrics() {
    try {
        const response = await fetch(`${API_BASE_URL}/metrics`);
        const data = await response.json();
        
        if (response.ok) {
            if (data.metrics && Object.keys(data.metrics).length > 0) {
                metricsData = data;
                displayMetrics();
            } else {
                const container = document.getElementById('metricsContainer');
                if (container) {
                    container.innerHTML = `
                        <div class="instruction-card">
                            <p>📈 Click <strong>"Evaluate Models"</strong> button to calculate and display performance metrics.</p>
                            <p>Metrics include: MAE (Mean Absolute Error), RMSE (Root Mean Squared Error), and MAPE (Mean Absolute Percentage Error)</p>
                            ${data.message ? `<p style="color: #667eea; margin-top: 10px;"><em>${data.message}</em></p>` : ''}
                        </div>
                    `;
                }
            }
        } else {
            // Handle error response
            const container = document.getElementById('metricsContainer');
            if (container) {
                const errorMsg = data.detail || data.message || 'Unknown error';
                container.innerHTML = `
                    <div class="instruction-card">
                        <p>📈 Click <strong>"Evaluate Models"</strong> button to calculate and display performance metrics.</p>
                        <p style="color: #d32f2f;"><em>${errorMsg}</em></p>
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Error loading metrics:', error);
        const container = document.getElementById('metricsContainer');
        if (container) {
            container.innerHTML = `
                <div class="instruction-card">
                    <p>📈 Click <strong>"Evaluate Models"</strong> button to calculate and display performance metrics.</p>
                    <p style="color: #d32f2f;">Error: ${error.message}. Make sure the server is running.</p>
                </div>
            `;
        }
    }
}

async function loadForecasts() {
    try {
        const response = await fetch(`${API_BASE_URL}/forecasts`);
        const data = await response.json();
        
        if (response.ok) {
            if (data.forecasts && Object.keys(data.forecasts).length > 0) {
                forecastsData = data.forecasts;
                displayForecasts();
            } else {
                const container = document.getElementById('forecastsContainer');
                if (container) {
                    container.innerHTML = `
                        <div class="instruction-card">
                            <p>🔮 Click <strong>"Generate Forecasts"</strong> button to create 30-day traffic predictions.</p>
                            <p>Forecasts will be displayed as interactive charts for each junction.</p>
                            ${data.message ? `<p style="color: #667eea; margin-top: 10px;"><em>${data.message}</em></p>` : ''}
                        </div>
                    `;
                }
            }
        } else {
            // Handle error response
            const container = document.getElementById('forecastsContainer');
            if (container) {
                const errorMsg = data.detail || data.message || 'Unknown error';
                container.innerHTML = `
                    <div class="instruction-card">
                        <p>🔮 Click <strong>"Generate Forecasts"</strong> button to create 30-day traffic predictions.</p>
                        <p style="color: #d32f2f;"><em>${errorMsg}</em></p>
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Error loading forecasts:', error);
        const container = document.getElementById('forecastsContainer');
        if (container) {
            container.innerHTML = `
                <div class="instruction-card">
                    <p>🔮 Click <strong>"Generate Forecasts"</strong> button to create 30-day traffic predictions.</p>
                    <p style="color: #d32f2f;">Error: ${error.message}. Make sure the server is running.</p>
                </div>
            `;
        }
    }
}

function displayMetrics() {
    const container = document.getElementById('metricsContainer');
    
    if (!metricsData || !metricsData.metrics || Object.keys(metricsData.metrics).length === 0) {
        container.innerHTML = '<p class="loading">No metrics available. Please evaluate models first.</p>';
        return;
    }
    
    container.innerHTML = '';
    
    // Display summary
    if (metricsData.summary) {
        const summaryCard = createMetricCard(
            'Overall Average',
            metricsData.summary.average_mape ? `${metricsData.summary.average_mape.toFixed(2)}%` : 'N/A',
            `MAE: ${metricsData.summary.average_mae ? metricsData.summary.average_mae.toFixed(2) : 'N/A'} | RMSE: ${metricsData.summary.average_rmse ? metricsData.summary.average_rmse.toFixed(2) : 'N/A'}`
        );
        container.appendChild(summaryCard);
    }
    
    // Display metrics for each junction
    for (const [junction, metrics] of Object.entries(metricsData.metrics)) {
        const mapeValue = metrics.mape ? `${metrics.mape.toFixed(2)}%` : 'N/A';
        const card = createMetricCard(junction, mapeValue, `MAE: ${metrics.mae.toFixed(2)} | RMSE: ${metrics.rmse.toFixed(2)}`);
        container.appendChild(card);
    }
}

function createMetricCard(title, value, subtitle) {
    const card = document.createElement('div');
    card.className = 'metric-card';
    card.innerHTML = `
        <h3>${title}</h3>
        <div class="metric-value">${value}</div>
        <div class="metric-label">${subtitle}</div>
    `;
    return card;
}

function displayForecasts() {
    const container = document.getElementById('forecastsContainer');
    
    if (!forecastsData || Object.keys(forecastsData).length === 0) {
        container.innerHTML = '<p class="loading">No forecasts available. Please generate forecasts first.</p>';
        return;
    }
    
    container.innerHTML = '';
    
    for (const [junction, forecast] of Object.entries(forecastsData)) {
        const card = createForecastCard(junction, forecast);
        container.appendChild(card);
    }
}

function createForecastCard(junction, forecast) {
    const card = document.createElement('div');
    card.className = 'forecast-card';
    
    const canvas = document.createElement('canvas');
    canvas.id = `chart-${junction}`;
    
    card.innerHTML = `
        <h3>${junction}</h3>
        <div class="chart-container">
            <canvas id="chart-${junction}"></canvas>
        </div>
    `;
    
    // Create chart after card is added to DOM
    setTimeout(() => {
        createForecastChart(junction, forecast, canvas.id);
    }, 100);
    
    return card;
}

function createForecastChart(junction, forecast, canvasId) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    // Format dates for display
    const dates = forecast.dates.map(d => {
        const date = new Date(d);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    const forecastValues = forecast.forecast;
    const lowerBound = forecast.lower_bound || [];
    const upperBound = forecast.upper_bound || [];
    
    const datasets = [{
        label: 'Forecast',
        data: forecastValues,
        borderColor: 'rgb(102, 126, 234)',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
    }];
    
    // Add confidence interval if available
    if (lowerBound.length > 0 && upperBound.length > 0) {
        datasets.push({
            label: 'Upper Bound',
            data: upperBound,
            borderColor: 'rgba(102, 126, 234, 0.3)',
            backgroundColor: 'rgba(102, 126, 234, 0.05)',
            borderWidth: 1,
            fill: '+1',
            tension: 0.4,
            pointRadius: 0
        });
        datasets.push({
            label: 'Lower Bound',
            data: lowerBound,
            borderColor: 'rgba(102, 126, 234, 0.3)',
            backgroundColor: 'transparent',
            borderWidth: 1,
            fill: false,
            tension: 0.4,
            pointRadius: 0
        });
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        title: function(context) {
                            return 'Day ' + (context[0].dataIndex + 1) + ': ' + dates[context[0].dataIndex];
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Traffic Count'
                    },
                    beginAtZero: false
                }
            }
        }
    });
}

async function loadEDAPlots() {
    const plots = [
        { id: 'trendsPlot', name: 'traffic_trends.png' },
        { id: 'holidaysPlot', name: 'working_days_vs_holidays.png' },
        { id: 'peakHoursPlot', name: 'peak_hours.png' },
        { id: 'seasonalPlot', name: 'seasonal_patterns.png' }
    ];
    
    let loadedCount = 0;
    const edaInstruction = document.getElementById('edaInstruction');
    
    for (const plot of plots) {
        const img = document.getElementById(plot.id);
        if (img) {
            img.src = `${API_BASE_URL}/plots/${plot.name}`;
            img.onload = () => {
                img.classList.add('loaded');
                loadedCount++;
                // Hide instruction when at least one plot loads
                if (loadedCount > 0 && edaInstruction) {
                    edaInstruction.style.display = 'none';
                }
            };
            img.onerror = () => {
                // Plot not available yet
                img.style.display = 'none';
            };
        }
    }
    
    // If no plots loaded, show instruction
    setTimeout(() => {
        if (loadedCount === 0 && edaInstruction) {
            edaInstruction.style.display = 'block';
        }
    }, 2000);
}

