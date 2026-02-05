/**
 * MobileAgent Web UI - Main JavaScript
 * Handles device listing, task management, i18n, and UI interactions.
 */

// =============================================================================
// Internationalization (i18n)
// =============================================================================

const i18n = {
    'zh-TW': {
        // Header
        refresh: '重新整理',

        // Device table
        connectedDevices: '已連接裝置',
        loadingDevices: '載入裝置中...',
        noDevices: '無連接裝置',
        noDevicesHint: '請透過 USB 連接 Android 裝置並啟用 USB 偵錯。',
        retry: '重試',
        serial: '序號',
        status: '狀態',
        model: '型號',
        task: '任務',
        taskStatus: '任務狀態',
        actions: '操作',

        // Task history
        taskHistory: '任務歷史',
        device: '裝置',
        prompt: '提示詞',
        duration: '執行時間',
        created: '建立時間',
        noTasks: '尚無任務',

        // Task modal
        newTask: '新增任務',
        cliTool: 'CLI 工具',
        modelLabel: '模型',
        taskPrompt: '任務提示詞',
        taskPromptHint: '描述您希望 AI 代理在此裝置上執行的操作。',
        commandPreview: '命令預覽',
        cancel: '取消',
        execute: '執行',

        // Output modal
        taskOutput: '任務輸出',
        cancelTask: '取消任務',
        close: '關閉',

        // Status
        online: '在線',
        offline: '離線',
        idle: '待機',
        pending: '等待中',
        running: '執行中',
        completed: '已完成',
        failed: '失敗',
        cancelled: '已取消',
        awaiting: '等待輸入',

        // Buttons
        newTaskBtn: '新增任務',
        viewOutput: '查看輸出',

        // Final Answer
        finalResult: '最終結果',
        taskSuccess: '任務完成',
        taskFailed: '任務失敗',
        awaitingInput: '等待輸入',
        statusUnknown: '結果待確認',
        statusUnknownDesc: '任務已結束，但未能取得明確的結果回報',
    },
    'en': {
        // Header
        refresh: 'Refresh',

        // Device table
        connectedDevices: 'Connected Devices',
        loadingDevices: 'Loading devices...',
        noDevices: 'No Devices Connected',
        noDevicesHint: 'Connect an Android device via USB and enable USB debugging.',
        retry: 'Retry',
        serial: 'Serial',
        status: 'Status',
        model: 'Model',
        task: 'Task',
        taskStatus: 'Task Status',
        actions: 'Actions',

        // Task history
        taskHistory: 'Task History',
        device: 'Device',
        prompt: 'Prompt',
        duration: 'Duration',
        created: 'Created',
        noTasks: 'No tasks yet',

        // Task modal
        newTask: 'New Task',
        cliTool: 'CLI Tool',
        modelLabel: 'Model',
        taskPrompt: 'Task Prompt',
        taskPromptHint: 'Describe what you want the agent to do on this device.',
        commandPreview: 'Command Preview',
        cancel: 'Cancel',
        execute: 'Execute',

        // Output modal
        taskOutput: 'Task Output',
        cancelTask: 'Cancel Task',
        close: 'Close',

        // Status
        online: 'Online',
        offline: 'Offline',
        idle: 'Idle',
        pending: 'Pending',
        running: 'Running',
        completed: 'Completed',
        failed: 'Failed',
        cancelled: 'Cancelled',
        awaiting: 'Awaiting Input',

        // Buttons
        newTaskBtn: 'New Task',
        viewOutput: 'View Output',

        // Final Answer
        finalResult: 'Final Result',
        taskSuccess: 'Task Completed',
        taskFailed: 'Task Failed',
        awaitingInput: 'Awaiting Input',
        statusUnknown: 'Status Unknown',
        statusUnknownDesc: 'Task ended but no clear result was reported',
    }
};

let currentLang = localStorage.getItem('lang') || 'zh-TW';

/**
 * Set language and update UI.
 */
function setLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);
    applyLanguage();
}

/**
 * Apply current language to all elements with data-i18n attribute.
 */
function applyLanguage() {
    const langData = i18n[currentLang] || i18n['en'];

    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (langData[key]) {
            el.textContent = langData[key];
        }
    });

    // Update language dropdown label
    document.getElementById('currentLangLabel').textContent = currentLang === 'zh-TW' ? '繁中' : 'EN';

    // Update placeholder
    const promptInput = document.getElementById('taskPrompt');
    if (promptInput) {
        promptInput.placeholder = currentLang === 'zh-TW'
            ? '例如：打開 Chrome 搜尋最新新聞'
            : 'e.g., Open Chrome and search for latest news';
    }
}

/**
 * Get translated text.
 */
function t(key) {
    const langData = i18n[currentLang] || i18n['en'];
    return langData[key] || key;
}

// =============================================================================
// Global State
// =============================================================================

let devices = [];
let tasks = [];
let cliOptions = {};
let refreshInterval = null;
let outputPollInterval = null;
let currentViewingTaskId = null;

// =============================================================================
// Configuration
// =============================================================================

let appConfig = {
    autoRefreshInterval: 60  // Default 60 seconds
};

/**
 * Fetch app configuration from server.
 */
async function fetchConfig() {
    try {
        const response = await fetch('/api/config');
        const data = await response.json();

        if (data.success && data.config) {
            appConfig = {
                autoRefreshInterval: data.config.autoRefreshInterval || 60
            };
        }
        return appConfig;
    } catch (error) {
        console.error('Error fetching config:', error);
        return appConfig;
    }
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Fetch CLI options (tools and models).
 */
async function fetchCliOptions() {
    try {
        const response = await fetch('/api/cli-options');
        const data = await response.json();

        if (data.success) {
            cliOptions = data.options;
            return data.options;
        }
        return {};
    } catch (error) {
        console.error('Error fetching CLI options:', error);
        return {};
    }
}

/**
 * Fetch list of connected devices.
 */
async function fetchDevices() {
    try {
        const response = await fetch('/api/devices');
        const data = await response.json();

        if (data.success) {
            return data.devices;
        } else {
            console.error('Failed to fetch devices:', data.error);
            return [];
        }
    } catch (error) {
        console.error('Error fetching devices:', error);
        return [];
    }
}

/**
 * Fetch all tasks.
 */
async function fetchTasks() {
    try {
        const response = await fetch('/api/tasks');
        const data = await response.json();

        if (data.success) {
            return data.tasks;
        } else {
            console.error('Failed to fetch tasks:', data.error);
            return [];
        }
    } catch (error) {
        console.error('Error fetching tasks:', error);
        return [];
    }
}

/**
 * Fetch specific task output.
 */
async function fetchTaskOutput(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}/output`);
        const data = await response.json();

        if (data.success) {
            return data;
        }
        return null;
    } catch (error) {
        console.error('Error fetching task output:', error);
        return null;
    }
}

/**
 * Create a new task.
 */
async function createTask(deviceSerial, prompt, cliTool, model) {
    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                device_serial: deviceSerial,
                prompt: prompt,
                cli_tool: cliTool,
                model: model
            })
        });

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error creating task:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Cancel a task.
 */
async function cancelTask(taskId) {
    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: 'DELETE'
        });

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error cancelling task:', error);
        return { success: false, error: error.message };
    }
}

// =============================================================================
// UI Rendering Functions
// =============================================================================

/**
 * Refresh device list and update UI.
 */
async function refreshDevices() {
    const btnRefresh = document.getElementById('btnRefresh');
    const loadingState = document.getElementById('loadingState');
    const emptyState = document.getElementById('emptyState');
    const tableContainer = document.getElementById('deviceTableContainer');

    // Show loading spinner on button
    btnRefresh.disabled = true;
    btnRefresh.innerHTML = `<i class="fas fa-spinner fa-spin"></i><span class="ms-1 d-none d-sm-inline">...</span>`;

    // Fetch devices
    devices = await fetchDevices();

    // Also fetch tasks to update history
    tasks = await fetchTasks();
    renderTaskHistory();

    // Update last update time
    updateLastUpdateTime();

    // Update device count badge
    document.getElementById('deviceCount').textContent = devices.length;

    // Show appropriate state
    loadingState.classList.add('d-none');

    if (devices.length === 0) {
        emptyState.classList.remove('d-none');
        tableContainer.classList.add('d-none');
    } else {
        emptyState.classList.add('d-none');
        tableContainer.classList.remove('d-none');
        renderDeviceTable();
    }

    // Reset button
    btnRefresh.disabled = false;
    btnRefresh.innerHTML = `<i class="fas fa-sync-alt"></i><span class="ms-1 d-none d-sm-inline">${t('refresh')}</span>`;
}

/**
 * Render device table rows.
 */
function renderDeviceTable() {
    const tbody = document.getElementById('deviceTableBody');
    tbody.innerHTML = '';

    devices.forEach(device => {
        const row = document.createElement('tr');

        // Status badge
        const statusClass = device.status === 'online' ? 'status-online' : 'status-offline';
        const statusText = device.status === 'online' ? t('online') : device.status;

        // Task info
        let taskCell = '<span class="text-muted">-</span>';
        let taskStatusCell = `<span class="status-badge status-idle">${t('idle')}</span>`;
        let hasRunningTask = false;

        if (device.task) {
            const promptShort = device.task.prompt.length > 40
                ? device.task.prompt.substring(0, 40) + '...'
                : device.task.prompt;

            taskCell = `<span class="task-prompt" title="${escapeHtml(device.task.prompt)}">${escapeHtml(promptShort)}</span>`;

            const effectiveStatus = getEffectiveTaskStatus(device.task);
            const taskStatusClass = getTaskStatusClass(effectiveStatus);
            const taskStatusText = t(effectiveStatus);
            taskStatusCell = `<span class="status-badge ${taskStatusClass}">${taskStatusText}</span>`;

            if (device.task.status === 'pending' || device.task.status === 'running') {
                hasRunningTask = true;
            }
        }

        // Actions
        let actionsHtml = '';
        if (device.status === 'online') {
            if (hasRunningTask) {
                actionsHtml = `
                    <div class="btn-group-actions">
                        <button class="btn btn-outline-primary btn-sm" onclick="viewTaskOutput('${device.task.id}')" title="${t('viewOutput')}">
                            <i class="fas fa-terminal"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-sm" onclick="confirmCancelTask('${device.task.id}')" title="${t('cancelTask')}">
                            <i class="fas fa-stop"></i>
                        </button>
                    </div>
                `;
            } else {
                actionsHtml = `
                    <button class="btn btn-primary btn-sm" onclick="openTaskModal('${device.serial}', '${escapeHtml(device.model)}')">
                        <i class="fas fa-play me-1"></i>${t('newTaskBtn')}
                    </button>
                `;
            }
        } else {
            actionsHtml = '<span class="text-muted">-</span>';
        }

        row.innerHTML = `
            <td data-label="${t('serial')}"><code>${device.serial}</code></td>
            <td data-label="${t('status')}"><span class="status-badge ${statusClass}"><span class="status-dot ${device.status}"></span>${statusText}</span></td>
            <td data-label="${t('model')}">${escapeHtml(device.model)}</td>
            <td data-label="${t('task')}">${taskCell}</td>
            <td data-label="${t('taskStatus')}">${taskStatusCell}</td>
            <td data-label="${t('actions')}">${actionsHtml}</td>
        `;

        tbody.appendChild(row);
    });
}

/**
 * Render task history table.
 */
function renderTaskHistory() {
    const tbody = document.getElementById('taskHistoryBody');

    // Clear existing rows
    tbody.innerHTML = '';

    if (tasks.length === 0) {
        tbody.innerHTML = `<tr id="noTasksRow"><td colspan="7" class="text-center text-muted py-4">${t('noTasks')}</td></tr>`;
        return;
    }

    // Sort by created_at desc
    const sortedTasks = [...tasks].sort((a, b) => {
        return new Date(b.created_at) - new Date(a.created_at);
    });

    sortedTasks.forEach(task => {
        const row = document.createElement('tr');

        const promptShort = task.prompt.length > 50
            ? task.prompt.substring(0, 50) + '...'
            : task.prompt;

        const effectiveStatus = getEffectiveTaskStatus(task);
        const statusClass = getTaskStatusClass(effectiveStatus);
        const statusText = t(effectiveStatus);

        const createdAt = formatDateTime(task.created_at);

        // 計算執行時間
        let durationText = '--';
        if (task.started_at) {
            const started = new Date(task.started_at);
            if (task.finished_at) {
                const finished = new Date(task.finished_at);
                const durationSec = (finished - started) / 1000;
                durationText = formatDuration(durationSec);
            } else if (task.status === 'running') {
                // 任務還在執行中
                const durationSec = (new Date() - started) / 1000;
                durationText = formatDuration(durationSec) + ' ⏱';
            }
        }

        let actionsHtml = `
            <button class="btn btn-outline-secondary btn-sm" onclick="viewTaskOutput('${task.id}')" title="${t('viewOutput')}">
                <i class="fas fa-terminal"></i>
            </button>
        `;

        if (task.status === 'pending' || task.status === 'running') {
            actionsHtml += `
                <button class="btn btn-outline-danger btn-sm ms-1" onclick="confirmCancelTask('${task.id}')" title="${t('cancel')}">
                    <i class="fas fa-stop"></i>
                </button>
            `;
        }

        row.innerHTML = `
            <td><code>${task.id}</code></td>
            <td><code class="text-muted">${task.device_serial}</code></td>
            <td><span class="task-prompt" title="${escapeHtml(task.prompt)}">${escapeHtml(promptShort)}</span></td>
            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            <td><span class="text-muted small">${durationText}</span></td>
            <td>${createdAt}</td>
            <td>${actionsHtml}</td>
        `;

        tbody.appendChild(row);
    });
}

/**
 * Update last update timestamp.
 */
function updateLastUpdateTime() {
    const el = document.getElementById('lastUpdate');
    const now = new Date();
    el.textContent = now.toLocaleTimeString();
}

/**
 * Update model select options based on selected CLI tool.
 */
function updateModelOptions() {
    const cliTool = document.getElementById('taskCliTool').value;
    const modelSelect = document.getElementById('taskModel');

    modelSelect.innerHTML = '';

    if (cliOptions[cliTool]) {
        cliOptions[cliTool].models.forEach(model => {
            const option = document.createElement('option');
            option.value = model.id;
            option.textContent = model.name;
            if (model.default) {
                option.selected = true;
            }
            modelSelect.appendChild(option);
        });
    }

    updateCommandPreview();
}

// =============================================================================
// Modal Functions
// =============================================================================

/**
 * Open task creation modal.
 */
function openTaskModal(serial, model) {
    document.getElementById('taskDeviceSerial').value = serial;
    document.getElementById('taskDeviceDisplay').value = `${serial} (${model})`;
    document.getElementById('taskPrompt').value = '';
    document.getElementById('taskCliTool').value = 'gemini';

    updateModelOptions();

    const modal = new bootstrap.Modal(document.getElementById('taskModal'));
    modal.show();
}

/**
 * Update command preview in modal.
 */
function updateCommandPreview() {
    const prompt = document.getElementById('taskPrompt').value.trim() || 'Your task prompt here';
    const cliTool = document.getElementById('taskCliTool').value;
    const model = document.getElementById('taskModel').value;

    let command = '';
    if (cliTool === 'gemini') {
        // 當 model 為空時使用 command_default 格式
        if (model) {
            command = `gemini -m ${model} -p "${prompt}" --yolo`;
        } else {
            command = `gemini -p "${prompt}" --yolo`;
        }
    } else if (cliTool === 'claude') {
        if (model) {
            command = `claude --model ${model} -p "${prompt}" --dangerously-skip-permissions`;
        } else {
            command = `claude -p "${prompt}" --dangerously-skip-permissions`;
        }
    } else if (cliTool === 'codex') {
        if (model) {
            command = `codex exec -m ${model} --full-auto --skip-git-repo-check "${prompt}"`;
        } else {
            command = `codex exec --full-auto --skip-git-repo-check "${prompt}"`;
        }
    }

    document.getElementById('commandPreview').textContent = command;
}

/**
 * Submit new task from modal.
 */
async function submitTask() {
    const serial = document.getElementById('taskDeviceSerial').value;
    const prompt = document.getElementById('taskPrompt').value.trim();
    const cliTool = document.getElementById('taskCliTool').value;
    const model = document.getElementById('taskModel').value;

    if (!prompt) {
        alert(currentLang === 'zh-TW' ? '請輸入任務提示詞。' : 'Please enter a task prompt.');
        return;
    }

    const btnSubmit = document.getElementById('btnSubmitTask');
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = `<i class="fas fa-spinner fa-spin me-1"></i>${currentLang === 'zh-TW' ? '執行中...' : 'Executing...'}`;

    const result = await createTask(serial, prompt, cliTool, model);

    if (result.success) {
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('taskModal'));
        modal.hide();

        // Refresh device list
        await refreshDevices();

        // Optionally show output modal for the new task
        viewTaskOutput(result.task_id);
    } else {
        alert((currentLang === 'zh-TW' ? '建立任務失敗: ' : 'Failed to create task: ') + result.error);
    }

    btnSubmit.disabled = false;
    btnSubmit.innerHTML = `<i class="fas fa-play me-1"></i>${t('execute')}`;
}

/**
 * View task output in modal.
 */
async function viewTaskOutput(taskId) {
    currentViewingTaskId = taskId;

    const modal = new bootstrap.Modal(document.getElementById('outputModal'));
    modal.show();

    // Set initial state
    document.getElementById('outputTaskId').textContent = `Task: ${taskId}`;
    document.getElementById('outputContent').textContent = currentLang === 'zh-TW' ? '載入中...' : 'Loading...';
    document.getElementById('outputStatusBadge').textContent = '...';
    document.getElementById('outputStatusBadge').className = 'badge bg-secondary';

    // Hide Final Answer container initially
    document.getElementById('finalAnswerContainer').classList.add('d-none');

    // Start polling for output
    await pollTaskOutput();
    startOutputPolling();
}

/**
 * Parse final answer from output text.
 * Returns object with { found, content, status } or null if not found.
 * 
 * IMPORTANT: Only search for FINAL_ANSWER in the AI response portion,
 * not in the prompt instruction template. The AI response starts after
 * "mcp startup: ready:" line.
 */
function parseFinalAnswer(output) {
    if (!output) return null;

    const startTag = '<<FINAL_ANSWER>>';
    const endTag = '<<END_FINAL_ANSWER>>';

    // 找到 AI 回應開始的位置（在 MCP ready 之後）
    // 這樣可以避免誤解析 prompt 中的 instruction 模板
    const mcpReadyMarkers = [
        'mcp startup: ready:',
        'mcp: ready',
        'thinking\n'  // Codex 開始思考的標記
    ];
    
    let aiResponseStart = 0;
    for (const marker of mcpReadyMarkers) {
        const idx = output.indexOf(marker);
        if (idx !== -1) {
            aiResponseStart = Math.max(aiResponseStart, idx);
        }
    }

    // 只在 AI 回應部分搜尋 FINAL_ANSWER
    const aiResponsePortion = output.substring(aiResponseStart);
    const startIndex = aiResponsePortion.lastIndexOf(startTag);
    if (startIndex === -1) return null;

    const contentStart = startIndex + startTag.length;
    const endIndex = aiResponsePortion.indexOf(endTag, contentStart);
    if (endIndex === -1) return null;

    const content = aiResponsePortion.substring(contentStart, endIndex).trim();

    // 檢查是否是 prompt 模板中的範例文字
    if (content === 'Your final answer or result here (be concise but complete)') {
        return null;  // 這是模板，不是真正的回答
    }

    // Determine status based on content
    let status = 'success';
    if (content.startsWith('TASK_FAILED')) {
        status = 'failed';
    } else if (content.startsWith('AWAITING_INPUT')) {
        status = 'awaiting';
    }

    return { found: true, content, status };
}

/**
 * Render markdown content safely.
 * Uses marked.js if available, falls back to plain text.
 */
function renderMarkdown(text) {
    if (typeof marked !== 'undefined' && marked.parse) {
        // Configure marked for security
        marked.setOptions({
            breaks: true,      // Convert \n to <br>
            gfm: true,         // GitHub Flavored Markdown
            headerIds: false,  // Disable header IDs for cleaner output
            mangle: false      // Don't mangle email addresses
        });
        return marked.parse(text);
    }
    // Fallback: escape HTML and convert newlines
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\n/g, '<br>');
}

/**
 * Update Final Answer display in the modal.
 */
function updateFinalAnswerDisplay(taskStatus, output) {
    const container = document.getElementById('finalAnswerContainer');
    const header = document.getElementById('finalAnswerHeader');
    const label = document.getElementById('finalAnswerLabel');
    const content = document.getElementById('finalAnswerContent');

    // Only show for completed/failed/cancelled tasks
    const isTaskEnded = ['completed', 'failed', 'cancelled'].includes(taskStatus);

    if (!isTaskEnded) {
        container.classList.add('d-none');
        return;
    }

    const parsed = parseFinalAnswer(output);

    container.classList.remove('d-none');

    if (parsed && parsed.found) {
        // Show parsed final answer
        let statusClass, labelText, iconClass;

        switch (parsed.status) {
            case 'failed':
                statusClass = 'status-failed';
                labelText = t('taskFailed');
                iconClass = 'fas fa-times-circle';
                break;
            case 'awaiting':
                statusClass = 'status-awaiting';
                labelText = t('awaitingInput');
                iconClass = 'fas fa-question-circle';
                break;
            default:
                statusClass = 'status-success';
                labelText = t('taskSuccess');
                iconClass = 'fas fa-check-circle';
        }

        header.className = `final-answer-header ${statusClass}`;
        header.innerHTML = `<i class="${iconClass}"></i><span>${labelText}</span>`;
        content.className = `final-answer-content ${statusClass}`;
        // Render markdown content
        content.innerHTML = renderMarkdown(parsed.content);
    } else {
        // Show "Status Unknown" message
        header.className = 'final-answer-header status-unknown';
        header.innerHTML = `<i class="fas fa-question-circle"></i><span>${t('statusUnknown')}</span>`;
        content.className = 'final-answer-content status-unknown';
        content.innerHTML = `<div class="final-answer-unknown">
            <i class="fas fa-exclamation-triangle"></i>
            <span>${t('statusUnknownDesc')}</span>
        </div>`;
    }
}

/**
 * Colorize output text based on content patterns.
 * Returns HTML string with colored spans.
 */
function colorizeOutput(text) {
    if (!text) return '';

    // Escape HTML first
    const escaped = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Split into lines and process each
    const lines = escaped.split('\n');
    const colorizedLines = lines.map(line => {
        // ===== Codex-specific patterns =====
        
        // MCP tool success (green) - e.g., "filesystem.read_text_file(...) success in 4ms"
        // Supports tool names with hyphens like mobile-mcp.mobile_click_on_screen
        if (/^[\w-]+\.[\w_]+\([^)]*\) success in \d+m?s/.test(line)) {
            return `<span class="output-success">${line}</span>`;
        }
        
        // MCP tool call (cyan) - e.g., "tool mobile-mcp.mobile_list_elements({...})"
        if (/^tool [\w-]+\.[\w_]+\(/.test(line)) {
            return `<span class="output-tool">${line}</span>`;
        }
        
        // AI thinking block label (dim)
        if (/^thinking$/.test(line)) {
            return `<span class="output-dim">${line}</span>`;
        }
        
        // AI thinking content (dim) - lines starting with ** inside thinking blocks
        if (/^\*\*.*\*\*$/.test(line)) {
            return `<span class="output-dim">${line}</span>`;
        }
        
        // MCP startup messages (dim) - e.g., "mcp: fetch starting", "mcp: ready"
        if (/^mcp[: ]/.test(line)) {
            return `<span class="output-dim">${line}</span>`;
        }
        
        // Codex header info (system purple) - workdir, model, provider, etc.
        if (/^(workdir:|model:|provider:|approval:|sandbox:|reasoning|session id:)/i.test(line)) {
            return `<span class="output-system">${line}</span>`;
        }
        
        // Codex version header
        if (/^OpenAI Codex v[\d.]+/.test(line) || /^-+$/.test(line)) {
            return `<span class="output-system">${line}</span>`;
        }
        
        // "codex" label (system)
        if (/^codex$/.test(line)) {
            return `<span class="output-system">${line}</span>`;
        }
        
        // User prompt label
        if (/^user$/.test(line)) {
            return `<span class="output-info">${line}</span>`;
        }
        
        // Token usage (dim)
        if (/^tokens used$/.test(line) || /^[\d,]+$/.test(line.trim())) {
            return `<span class="output-dim">${line}</span>`;
        }
        
        // ===== General patterns =====
        
        // Error patterns (red)
        if (/^Error:|error:|ERROR|Exception:|Traceback/i.test(line) ||
            /Error executing tool/i.test(line) ||
            /failed to|failure/i.test(line)) {
            return `<span class="output-error">${line}</span>`;
        }

        // Warning patterns (yellow)
        if (/^Warning:|warning:|WARN|Retrying/i.test(line) ||
            /quota will reset/i.test(line)) {
            return `<span class="output-warning">${line}</span>`;
        }

        // Default: no color (let it be readable default text)
        return line;
    });

    return colorizedLines.join('\n');
}

/**
 * Strip FINAL_ANSWER tags from output for cleaner display.
 * The tags are still parsed separately for the Final Answer container.
 * 
 * IMPORTANT: Only strip AI's FINAL_ANSWER, not the prompt instruction template.
 */
function stripFinalAnswerTags(output) {
    if (!output) return output;

    const startTag = '<<FINAL_ANSWER>>';
    const endTag = '<<END_FINAL_ANSWER>>';

    // 找到 AI 回應開始的位置
    const mcpReadyMarkers = [
        'mcp startup: ready:',
        'mcp: ready',
        'thinking\n'
    ];
    
    let aiResponseStart = 0;
    for (const marker of mcpReadyMarkers) {
        const idx = output.indexOf(marker);
        if (idx !== -1) {
            aiResponseStart = Math.max(aiResponseStart, idx);
        }
    }

    // 只在 AI 回應部分搜尋 FINAL_ANSWER
    const aiResponsePortion = output.substring(aiResponseStart);
    const relativeStartIndex = aiResponsePortion.lastIndexOf(startTag);
    if (relativeStartIndex === -1) return output;

    const startIndex = aiResponseStart + relativeStartIndex;
    const endIndex = output.indexOf(endTag, startIndex);
    if (endIndex === -1) return output;

    // 檢查是否是 prompt 模板中的範例文字
    const content = output.substring(startIndex + startTag.length, endIndex).trim();
    if (content === 'Your final answer or result here (be concise but complete)') {
        return output;  // 不移除模板
    }

    // Remove the entire FINAL_ANSWER block from output
    const beforeTag = output.substring(0, startIndex).trimEnd();
    const afterTag = output.substring(endIndex + endTag.length).trimStart();

    return beforeTag + (afterTag ? '\n' + afterTag : '');
}

/**
 * 格式化執行時間為人類可讀格式
 */
function formatDuration(seconds) {
    if (seconds === null || seconds === undefined) return '--';
    
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    
    if (mins === 0) {
        return `${secs}s`;
    } else if (mins < 60) {
        return `${mins}m ${secs}s`;
    } else {
        const hours = Math.floor(mins / 60);
        const remainingMins = mins % 60;
        return `${hours}h ${remainingMins}m ${secs}s`;
    }
}

/**
 * Poll task output and update modal.
 */
async function pollTaskOutput() {
    if (!currentViewingTaskId) return;

    const data = await fetchTaskOutput(currentViewingTaskId);

    if (!data) {
        document.getElementById('outputContent').textContent = currentLang === 'zh-TW' ? '載入輸出失敗。' : 'Failed to load output.';
        return;
    }

    // Update status badge
    const badge = document.getElementById('outputStatusBadge');
    const statusClass = getBootstrapBadgeClass(data.status);
    badge.className = `badge ${statusClass}`;
    badge.textContent = t(data.status);

    // Update duration display
    const durationEl = document.getElementById('outputDurationValue');
    if (data.duration !== null && data.duration !== undefined) {
        durationEl.textContent = formatDuration(data.duration);
    } else {
        durationEl.textContent = '--';
    }

    // Update output content (strip FINAL_ANSWER tags for cleaner display)
    let rawOutput = data.output || '';
    let displayOutput = stripFinalAnswerTags(rawOutput) || (currentLang === 'zh-TW' ? '尚無輸出' : 'No output yet');

    if (data.error) {
        displayOutput += `\n\nError: ${data.error}`;
    }

    // Use colorized HTML output
    document.getElementById('outputContent').innerHTML = colorizeOutput(displayOutput);

    // Scroll to bottom of output
    const outputEl = document.getElementById('outputContent');
    outputEl.scrollTop = outputEl.scrollHeight;

    // Update Final Answer display (use raw output for parsing)
    updateFinalAnswerDisplay(data.status, rawOutput);

    // Show/hide cancel button
    const btnCancel = document.getElementById('btnCancelTask');
    if (data.status === 'pending' || data.status === 'running') {
        btnCancel.classList.remove('d-none');
        btnCancel.onclick = () => confirmCancelTask(currentViewingTaskId);
    } else {
        btnCancel.classList.add('d-none');
        stopOutputPolling();
    }
}

/**
 * Start polling for task output.
 */
function startOutputPolling() {
    stopOutputPolling();
    outputPollInterval = setInterval(pollTaskOutput, 1000);
}

/**
 * Stop polling for task output.
 */
function stopOutputPolling() {
    if (outputPollInterval) {
        clearInterval(outputPollInterval);
        outputPollInterval = null;
    }
}

/**
 * Confirm and cancel a task.
 */
async function confirmCancelTask(taskId) {
    const confirmMsg = currentLang === 'zh-TW' ? '確定要取消此任務嗎？' : 'Are you sure you want to cancel this task?';
    if (!confirm(confirmMsg)) {
        return;
    }

    const result = await cancelTask(taskId);

    if (result.success) {
        await refreshDevices();
        if (currentViewingTaskId === taskId) {
            await pollTaskOutput();
        }
    } else {
        alert((currentLang === 'zh-TW' ? '取消任務失敗: ' : 'Failed to cancel task: ') + result.error);
    }
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Escape HTML entities.
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Extract AI's actual FINAL_ANSWER content from output.
 * Only searches in AI response portion (after MCP ready), not in prompt instruction.
 * Returns null if no valid FINAL_ANSWER found.
 */
function extractFinalAnswerContent(output) {
    if (!output) return null;
    
    const startTag = '<<FINAL_ANSWER>>';
    const endTag = '<<END_FINAL_ANSWER>>';
    
    // Find where AI response starts (after MCP ready)
    const aiStartMarkers = ['mcp startup: ready:', 'mcp: ready', '\nthinking\n'];
    let aiStart = 0;
    for (const marker of aiStartMarkers) {
        const idx = output.indexOf(marker);
        if (idx !== -1) {
            aiStart = Math.max(aiStart, idx);
        }
    }
    
    // Search only in AI response portion
    const aiResponse = output.substring(aiStart);
    
    // Find the LAST FINAL_ANSWER (the real one, not template)
    const startIdx = aiResponse.lastIndexOf(startTag);
    if (startIdx === -1) return null;
    
    const contentStart = startIdx + startTag.length;
    const endIdx = aiResponse.indexOf(endTag, contentStart);
    if (endIdx === -1) return null;
    
    const content = aiResponse.substring(contentStart, endIdx).trim();
    
    // Skip if it's the template text
    if (content === 'Your final answer or result here (be concise but complete)') {
        return null;
    }
    
    return content;
}

/**
 * Get effective task status by checking FINAL_ANSWER content.
 * Only checks the actual AI response, not prompt instruction template.
 */
function getEffectiveTaskStatus(task) {
    if (!task) return 'idle';

    // If status is completed, verify from FINAL_ANSWER content
    if (task.status === 'completed' && task.output) {
        const finalAnswer = extractFinalAnswerContent(task.output);
        if (finalAnswer) {
            // Check if FINAL_ANSWER starts with failure/awaiting indicators
            if (finalAnswer.startsWith('TASK_FAILED')) {
                return 'failed';
            }
            if (finalAnswer.startsWith('AWAITING_INPUT')) {
                return 'awaiting';
            }
        }
    }

    return task.status;
}

/**
 * Get CSS class for task status.
 */
function getTaskStatusClass(status) {
    const classes = {
        'pending': 'status-pending',
        'running': 'status-running',
        'completed': 'status-completed',
        'failed': 'status-failed',
        'cancelled': 'status-cancelled',
        'awaiting': 'status-pending'
    };
    return classes[status] || 'status-idle';
}

/**
 * Get Bootstrap badge class for status.
 */
function getBootstrapBadgeClass(status) {
    const classes = {
        'pending': 'bg-warning text-dark',
        'running': 'bg-primary',
        'completed': 'bg-success',
        'failed': 'bg-danger',
        'cancelled': 'bg-secondary'
    };
    return classes[status] || 'bg-secondary';
}

/**
 * Format datetime string.
 */
function formatDateTime(isoString) {
    if (!isoString) return '-';
    const date = new Date(isoString);
    return date.toLocaleString();
}

// =============================================================================
// Event Listeners
// =============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    // Apply saved language
    applyLanguage();

    // Fetch CLI options
    await fetchCliOptions();

    // Initial load
    refreshDevices();

    // Refresh button
    document.getElementById('btnRefresh').addEventListener('click', refreshDevices);

    // CLI tool change - update model options
    document.getElementById('taskCliTool').addEventListener('change', updateModelOptions);

    // Task form inputs - update command preview
    document.getElementById('taskPrompt').addEventListener('input', updateCommandPreview);
    document.getElementById('taskModel').addEventListener('change', updateCommandPreview);

    // Submit task button
    document.getElementById('btnSubmitTask').addEventListener('click', submitTask);

    // Output modal hidden - stop polling
    document.getElementById('outputModal').addEventListener('hidden.bs.modal', () => {
        stopOutputPolling();
        currentViewingTaskId = null;
    });

    // Clear history button
    document.getElementById('btnClearHistory').addEventListener('click', async () => {
        const confirmMsg = currentLang === 'zh-TW' ? '確定要清除所有任務歷史嗎？此操作無法復原。' : 'Are you sure you want to clear all task history? This cannot be undone.';
        if (!confirm(confirmMsg)) {
            return;
        }

        try {
            const response = await fetch('/api/tasks/clear', {
                method: 'POST'
            });
            const data = await response.json();

            if (data.success) {
                const successMsg = currentLang === 'zh-TW' ? `已清除 ${data.count} 筆任務` : data.message;
                alert(successMsg);
                await refreshDevices();
            } else {
                const errorMsg = currentLang === 'zh-TW' ? '清除失敗: ' : 'Failed to clear: ';
                alert(errorMsg + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error clearing history:', error);
            const errorMsg = currentLang === 'zh-TW' ? '清除失敗: ' : 'Failed to clear: ';
            alert(errorMsg + error.message);
        }
    });

    // Auto-refresh every 5 seconds
    refreshInterval = setInterval(refreshDevices, 6443);
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
    stopOutputPolling();
});
