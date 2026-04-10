const workflowForm = document.getElementById("workflow-form");
const workflowTableBody = document.getElementById("workflow-table-body");
const statusMessage = document.getElementById("status-message");
const emptyStateMarkup = `
    <tr id="workflow-empty-state">
        <td colspan="5" class="px-4 py-10 text-center text-sm text-slate-500">No workflows found.</td>
    </tr>
`;

let statusTimeoutId = null;

function normalizeResponseShape(response, body, fallbackMessage) {
    if (body && typeof body === "object" && "return_code" in body && "error_message" in body) {
        return {
            return_code: body.return_code,
            error_message: body.error_message,
            data: body.data ?? null,
        };
    }

    if (!response.ok) {
        return {
            return_code: -1,
            error_message: body?.error || fallbackMessage,
            data: body?.data ?? null,
        };
    }

    return {
        return_code: 0,
        error_message: null,
        data: body && typeof body === "object" && "data" in body ? body.data : body,
    };
}

async function requestJson(url, options = {}, fallbackMessage = "Request failed.") {
    try {
        const response = await fetch(url, options);
        let body = null;

        try {
            body = await response.json();
        } catch {
            body = null;
        }

        return normalizeResponseShape(response, body, fallbackMessage);
    } catch (error) {
        return {
            return_code: -1,
            error_message: error instanceof Error ? error.message : fallbackMessage,
            data: null,
        };
    }
}

function showStatus(message, isError = false) {
    if (!statusMessage) {
        return;
    }

    if (statusTimeoutId !== null) {
        window.clearTimeout(statusTimeoutId);
    }

    statusMessage.textContent = message;
    statusMessage.className = isError
        ? "mb-6 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-800 shadow-sm"
        : "mb-6 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800 shadow-sm";

    statusTimeoutId = window.setTimeout(() => {
        statusMessage.textContent = "";
        statusMessage.className = "mb-6 hidden rounded-2xl border px-4 py-3 text-sm font-medium shadow-sm";
        statusTimeoutId = null;
    }, 5000);
}

function renderWorkflows(workflows) {
    if (!workflowTableBody) {
        return;
    }

    if (!Array.isArray(workflows) || workflows.length === 0) {
        workflowTableBody.innerHTML = emptyStateMarkup;
        return;
    }

    const rows = workflows.map((workflow) => {
        const workflowId = workflow.workflow_id ?? workflow.id ?? "N/A";
        const workflowName = workflow.workflow_name || workflow.name || "N/A";
        const workflowType = workflow.workflow_type || workflow.type || "N/A";
        const createdBy = workflow.created_by || workflow.user || "System";

        return `
            <tr data-workflow-id="${workflowId}" class="transition hover:bg-slate-50">
                <td class="whitespace-nowrap px-4 py-4 font-medium text-slate-900">${workflowId}</td>
                <td class="px-4 py-4 text-slate-700">${workflowName}</td>
                <td class="px-4 py-4 text-slate-700">${workflowType}</td>
                <td class="px-4 py-4 text-slate-500">${createdBy}</td>
                <td class="px-4 py-4 text-right">
                    <button
                        type="button"
                        class="delete-workflow-button inline-flex items-center justify-center rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-rose-700 transition hover:border-rose-300 hover:bg-rose-100"
                        data-workflow-id="${workflowId}"
                    >
                        Delete
                    </button>
                </td>
            </tr>
        `;
    });

    workflowTableBody.innerHTML = rows.join("");
}

async function loadWorkflows() {
    if (!workflowTableBody) {
        return;
    }

    const result = await requestJson("/api/workflows", {}, "Failed to load workflows.");
    if (result.return_code !== 0) {
        console.error("Workflow load failed:", result.error_message);
        workflowTableBody.innerHTML = `
            <tr id="workflow-empty-state">
                <td colspan="5" class="px-4 py-10 text-center text-sm text-rose-600">Failed to load workflows.</td>
            </tr>
        `;
        showStatus(result.error_message || "Failed to load workflows.", true);
        return;
    }

    renderWorkflows(result.data);
}

async function addWorkflow() {
    if (!workflowForm) {
        return;
    }

    const formData = new FormData(workflowForm);
    const name = String(formData.get("name") || "").trim();
    const type = String(formData.get("type") || "").trim();

    if (!name || !type) {
        showStatus("Please enter both name and type.", true);
        return;
    }

    const payload = {
        name,
        type,
        description: "Added via Web UI",
        subtype: "Standard",
        user: "AdminUser",
    };

    const result = await requestJson(
        "/api/workflows",
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        },
        "Failed to add workflow."
    );

    if (result.return_code !== 0) {
        showStatus(result.error_message || "Failed to add workflow.", true);
        return;
    }

    workflowForm.reset();
    await loadWorkflows();
    showStatus("Workflow added successfully.");
}

async function deleteWorkflow(workflowId) {
    const confirmed = window.confirm(`Are you sure you want to delete workflow #${workflowId}?`);
    if (!confirmed) {
        return;
    }

    const result = await requestJson(
        `/api/workflows/${workflowId}`,
        { method: "DELETE" },
        "Failed to delete workflow."
    );

    if (result.return_code !== 0) {
        console.error("Workflow delete failed:", result.error_message);
        showStatus(result.error_message || "Failed to delete workflow.", true);
        return;
    }

    await loadWorkflows();
    showStatus(`Workflow #${workflowId} deleted.`);
}

function registerEventListeners() {
    if (workflowForm) {
        workflowForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            await addWorkflow();
        });
    }

    if (workflowTableBody) {
        workflowTableBody.addEventListener("click", async (event) => {
            const deleteButton = event.target.closest(".delete-workflow-button");
            if (!deleteButton) {
                return;
            }

            const workflowId = Number(deleteButton.dataset.workflowId);
            if (!Number.isNaN(workflowId)) {
                await deleteWorkflow(workflowId);
            }
        });
    }
}

function initializeWorkflowPage() {
    if (!workflowForm || !workflowTableBody) {
        return;
    }

    registerEventListeners();
    void loadWorkflows();
}

window.addEventListener("DOMContentLoaded", initializeWorkflowPage);