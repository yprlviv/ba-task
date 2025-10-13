// Facebook Ads Integration Dashboard JavaScript

// Global state
let currentWizardStep = 1;
let campaignData = {};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeChart();
    initializeEventListeners();
    updateDateTime();
    
    // Update time every minute
    setInterval(updateDateTime, 60000);
});

// Initialize Chart.js performance chart
function initializeChart() {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;

    // Sample data for the performance chart
    const data = {
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        datasets: [{
            label: 'Impressions',
            data: [12000, 19000, 15000, 25000],
            borderColor: '#667eea',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            tension: 0.4,
            fill: true
        }, {
            label: 'Clicks',
            data: [300, 450, 380, 600],
            borderColor: '#764ba2',
            backgroundColor: 'rgba(118, 75, 162, 0.1)',
            tension: 0.4,
            fill: true
        }]
    };

    new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time Period'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Count'
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

// Initialize event listeners
function initializeEventListeners() {
    // Campaign search functionality
    const searchInput = document.getElementById('campaignSearch');
    if (searchInput) {
        searchInput.addEventListener('input', filterCampaigns);
    }

    // Budget type radio buttons
    const budgetRadios = document.querySelectorAll('input[name="budgetType"]');
    budgetRadios.forEach(radio => {
        radio.addEventListener('change', handleBudgetTypeChange);
    });

    // Budget amount input
    const budgetAmountInput = document.getElementById('budgetAmount');
    if (budgetAmountInput) {
        budgetAmountInput.addEventListener('input', updateBudgetProjection);
    }

    // Date inputs
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    if (startDateInput && endDateInput) {
        startDateInput.addEventListener('change', updateBudgetProjection);
        endDateInput.addEventListener('change', updateBudgetProjection);
    }

    // Frequency cap checkbox
    const frequencyCapCheckbox = document.getElementById('enableFrequencyCap');
    if (frequencyCapCheckbox) {
        frequencyCapCheckbox.addEventListener('change', toggleFrequencyCap);
    }

    // Close modal when clicking outside
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-overlay')) {
            closeAllModals();
        }
        
        // Close action menus when clicking outside
        if (!e.target.closest('.action-menu') && !e.target.closest('.action-menu-btn')) {
            closeAllActionMenus();
        }
    });

    // Set default start date to tomorrow
    if (startDateInput) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        startDateInput.value = tomorrow.toISOString().split('T')[0];
        startDateInput.min = tomorrow.toISOString().split('T')[0];
    }
}

// Update date and time display
function updateDateTime() {
    const syncElements = document.querySelectorAll('.sync-status span');
    const now = new Date();
    const timeAgo = Math.floor((now - new Date(now.getTime() - 2 * 60000)) / 60000);
    
    syncElements.forEach(element => {
        element.textContent = `Last Sync: ${timeAgo}m ago`;
    });
}

// Campaign Management Functions
function openCampaignWizard() {
    const modal = document.getElementById('campaignWizardModal');
    if (modal) {
        modal.classList.add('show');
        resetWizard();
    }
}

function closeCampaignWizard() {
    const modal = document.getElementById('campaignWizardModal');
    if (modal) {
        modal.classList.remove('show');
        resetWizard();
    }
}

function resetWizard() {
    currentWizardStep = 1;
    campaignData = {};
    
    // Reset form
    const form = document.querySelector('.wizard-content');
    if (form) {
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            if (input.type === 'checkbox' || input.type === 'radio') {
                input.checked = input.defaultChecked;
            } else {
                input.value = input.defaultValue || '';
            }
        });
    }
    
    // Reset to first step
    showWizardStep(1);
    updateWizardNavigation();
}

function nextStep() {
    if (validateCurrentStep()) {
        saveCurrentStepData();
        
        if (currentWizardStep < 4) {
            currentWizardStep++;
            showWizardStep(currentWizardStep);
            updateWizardNavigation();
        } else {
            // Final step - create campaign
            createCampaign();
        }
    }
}

function previousStep() {
    if (currentWizardStep > 1) {
        currentWizardStep--;
        showWizardStep(currentWizardStep);
        updateWizardNavigation();
    }
}

function showWizardStep(step) {
    // Hide all steps
    const steps = document.querySelectorAll('.wizard-step');
    steps.forEach(stepEl => stepEl.classList.remove('active'));
    
    // Show current step
    const currentStepEl = document.getElementById(`step${step}`);
    if (currentStepEl) {
        currentStepEl.classList.add('active');
    }
    
    // Update step indicator
    const stepIndicator = document.getElementById('currentStep');
    if (stepIndicator) {
        stepIndicator.textContent = step;
    }
}

function updateWizardNavigation() {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (prevBtn) {
        prevBtn.style.display = currentWizardStep > 1 ? 'flex' : 'none';
    }
    
    if (nextBtn) {
        if (currentWizardStep === 4) {
            nextBtn.innerHTML = '<i class="fas fa-check"></i> Create Campaign';
        } else {
            nextBtn.innerHTML = 'Next <i class="fas fa-arrow-right"></i>';
        }
    }
}

function validateCurrentStep() {
    const currentStepEl = document.getElementById(`step${currentWizardStep}`);
    if (!currentStepEl) return false;
    
    const requiredInputs = currentStepEl.querySelectorAll('input[required], select[required]');
    let isValid = true;
    
    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = '#dc3545';
            isValid = false;
        } else {
            input.style.borderColor = '#dee2e6';
        }
    });
    
    if (!isValid) {
        showNotification('Please fill in all required fields', 'error');
    }
    
    return isValid;
}

function saveCurrentStepData() {
    const currentStepEl = document.getElementById(`step${currentWizardStep}`);
    if (!currentStepEl) return;
    
    const inputs = currentStepEl.querySelectorAll('input, select');
    inputs.forEach(input => {
        if (input.type === 'checkbox') {
            campaignData[input.id] = input.checked;
        } else if (input.type === 'radio' && input.checked) {
            campaignData[input.name] = input.value;
        } else if (input.type !== 'radio') {
            campaignData[input.id] = input.value;
        }
    });
}

async function createCampaign() {
    try {
        // Show loading state
        const nextBtn = document.getElementById('nextBtn');
        if (nextBtn) {
            nextBtn.disabled = true;
            nextBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
        }
        
        // Prepare campaign data for API
        const apiData = {
            name: campaignData.campaignName,
            objective: campaignData.campaignGoal,
            start_time: new Date(campaignData.startDate).toISOString(),
            stop_time: campaignData.endDate ? new Date(campaignData.endDate).toISOString() : null,
            budget_type: campaignData.budgetType === 'daily' ? 'daily_budget' : 'lifetime_budget',
            budget_amount: Math.round(parseFloat(campaignData.budgetAmount) * 100), // Convert to cents
            ad_account_id: 'act_123456789', // Demo account
            frequency_cap: campaignData.enableFrequencyCap ? {
                event: 'IMPRESSIONS',
                interval_days: 7,
                max_frequency: 3
            } : null
        };
        
        // Call API
        const response = await fetch('/api/v1/campaigns/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(apiData)
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification('Campaign created successfully!', 'success');
            closeCampaignWizard();
            
            // Add new campaign to the table
            addCampaignToTable(result);
        } else {
            const error = await response.json();
            showNotification(`Error: ${error.detail || 'Failed to create campaign'}`, 'error');
        }
    } catch (error) {
        console.error('Error creating campaign:', error);
        showNotification('Network error. Please try again.', 'error');
    } finally {
        // Reset button state
        const nextBtn = document.getElementById('nextBtn');
        if (nextBtn) {
            nextBtn.disabled = false;
            nextBtn.innerHTML = '<i class="fas fa-check"></i> Create Campaign';
        }
    }
}

// Campaign table functions
function addCampaignToTable(campaign) {
    const campaignsTable = document.querySelector('.campaigns-table');
    if (!campaignsTable) return;
    
    const campaignRow = document.createElement('div');
    campaignRow.className = 'campaign-row';
    campaignRow.dataset.campaignId = campaign.id;
    
    campaignRow.innerHTML = `
        <div class="col-name">
            <div class="campaign-name">${campaign.name}</div>
        </div>
        <div class="col-status">
            <span class="status-badge ${campaign.status.toLowerCase()}">
                <i class="fas fa-${getStatusIcon(campaign.status)}"></i> ${campaign.status}
            </span>
        </div>
        <div class="col-budget">$${(campaign.budget_amount / 100).toFixed(2)}/${campaign.budget_type === 'daily_budget' ? 'day' : 'total'}</div>
        <div class="col-spend">$0.00</div>
        <div class="col-actions">
            <button class="action-menu-btn" onclick="toggleActionMenu('${campaign.id}')">
                <i class="fas fa-ellipsis-v"></i>
            </button>
            <div class="action-menu" id="actionMenu${campaign.id}">
                <button onclick="editCampaign('${campaign.id}')">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button onclick="viewCampaign('${campaign.id}')">
                    <i class="fas fa-eye"></i> View
                </button>
                <button onclick="pauseCampaign('${campaign.id}')">
                    <i class="fas fa-pause"></i> Pause
                </button>
            </div>
        </div>
    `;
    
    campaignsTable.appendChild(campaignRow);
}

function getStatusIcon(status) {
    switch (status.toLowerCase()) {
        case 'active': return 'circle';
        case 'paused': return 'pause';
        case 'ended': return 'stop';
        case 'deleted': return 'trash';
        default: return 'circle';
    }
}

// Action menu functions
function toggleActionMenu(campaignId) {
    closeAllActionMenus();
    
    const menu = document.getElementById(`actionMenu${campaignId}`);
    if (menu) {
        menu.classList.toggle('show');
    }
}

function closeAllActionMenus() {
    const menus = document.querySelectorAll('.action-menu');
    menus.forEach(menu => menu.classList.remove('show'));
}

// Campaign actions
function editCampaign(campaignId) {
    closeAllActionMenus();
    showNotification(`Edit campaign ${campaignId} - Feature coming soon!`, 'info');
}

function viewCampaign(campaignId) {
    closeAllActionMenus();
    showNotification(`View campaign ${campaignId} - Feature coming soon!`, 'info');
}

function pauseCampaign(campaignId) {
    closeAllActionMenus();
    showNotification(`Pause campaign ${campaignId} - Feature coming soon!`, 'info');
}

function activateCampaign(campaignId) {
    closeAllActionMenus();
    showNotification(`Activate campaign ${campaignId} - Feature coming soon!`, 'info');
}

function duplicateCampaign(campaignId) {
    closeAllActionMenus();
    showNotification(`Duplicate campaign ${campaignId} - Feature coming soon!`, 'info');
}

// Search and filter functions
function filterCampaigns() {
    const searchTerm = document.getElementById('campaignSearch').value.toLowerCase();
    const campaignRows = document.querySelectorAll('.campaign-row');
    
    campaignRows.forEach(row => {
        const campaignName = row.querySelector('.campaign-name').textContent.toLowerCase();
        if (campaignName.includes(searchTerm)) {
            row.style.display = 'grid';
        } else {
            row.style.display = 'none';
        }
    });
}

// Form handling functions
function handleBudgetTypeChange(event) {
    const budgetType = event.target.value;
    const label = document.querySelector('label[for="budgetAmount"]');
    
    if (label) {
        label.textContent = budgetType === 'daily' ? 'Daily Budget Amount *' : 'Lifetime Budget Amount *';
    }
    
    updateBudgetProjection();
}

function updateBudgetProjection() {
    const budgetAmount = parseFloat(document.getElementById('budgetAmount')?.value) || 0;
    const startDate = document.getElementById('startDate')?.value;
    const endDate = document.getElementById('endDate')?.value;
    const budgetType = document.querySelector('input[name="budgetType"]:checked')?.value || 'daily';
    
    let duration = 0;
    let maxSpend = 0;
    
    if (startDate && endDate) {
        const start = new Date(startDate);
        const end = new Date(endDate);
        duration = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
    } else {
        duration = 92; // Default 3 months
    }
    
    if (budgetType === 'daily') {
        maxSpend = budgetAmount * duration;
    } else {
        maxSpend = budgetAmount;
    }
    
    // Update projection display
    const durationEl = document.getElementById('campaignDuration');
    const maxSpendEl = document.getElementById('maxSpend');
    
    if (durationEl) {
        durationEl.textContent = `${duration} days`;
    }
    
    if (maxSpendEl) {
        maxSpendEl.textContent = `$${maxSpend.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
}

function toggleFrequencyCap() {
    const checkbox = document.getElementById('enableFrequencyCap');
    const details = document.getElementById('frequencyCapDetails');
    
    if (checkbox && details) {
        details.style.display = checkbox.checked ? 'block' : 'none';
    }
}

// Navigation functions
function openReports() {
    showNotification('Reports dashboard - Feature coming soon!', 'info');
}

function openAccountManager() {
    showNotification('Account manager - Feature coming soon!', 'info');
}

// Utility functions
function closeAllModals() {
    const modals = document.querySelectorAll('.modal-overlay');
    modals.forEach(modal => modal.classList.remove('show'));
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="closeNotification(this)">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add styles if not already added
    if (!document.querySelector('#notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                padding: 1rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
                max-width: 400px;
                z-index: 3000;
                border-left: 4px solid;
                animation: slideIn 0.3s ease-out;
            }
            
            .notification-info { border-left-color: #17a2b8; }
            .notification-success { border-left-color: #28a745; }
            .notification-error { border-left-color: #dc3545; }
            .notification-warning { border-left-color: #ffc107; }
            
            .notification-content {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                flex: 1;
            }
            
            .notification-close {
                background: none;
                border: none;
                cursor: pointer;
                color: #6c757d;
                padding: 0.25rem;
                margin-left: 1rem;
            }
            
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(styles);
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            closeNotification(notification.querySelector('.notification-close'));
        }
    }, 5000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}

function closeNotification(button) {
    const notification = button.closest('.notification');
    if (notification) {
        notification.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }
}

// Add slide out animation
const slideOutStyles = document.createElement('style');
slideOutStyles.textContent = `
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(slideOutStyles);
