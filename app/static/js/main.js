const workflowForm = document.getElementById("workflow-form");
const workflowTableBody = document.getElementById("workflow-table-body");
const statusMessage = document.getElementById("status-message");
const workflowIdField = document.getElementById("workflow-id");
const workflowNameField = document.getElementById("name");
const workflowDescriptionField = document.getElementById("description");
const workflowTypeField = document.getElementById("type");
const workflowSubtypeField = document.getElementById("subtype");
const workflowSubmitButton = document.getElementById("workflow-submit-button");
const workflowCancelButton = document.getElementById("workflow-cancel-button");
const workflowFormEyebrow = document.getElementById("workflow-form-eyebrow");
const workflowFormTitle = document.getElementById("workflow-form-title");
const workflowFormDescription = document.getElementById("workflow-form-description");
const emptyStateMarkup = `
    <tr id="workflow-empty-state">
        <td colspan="7" class="px-4 py-10 text-center text-sm text-slate-500">No workflows found.</td>
    </tr>
`;

let statusTimeoutId = null;
let editingWorkflowId = null;
let workflowsById = new Map();

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

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function resetWorkflowForm() {
    if (!workflowForm) {
        return;
    }

    workflowForm.reset();

    if (workflowIdField) {
        workflowIdField.value = "";
    }

    editingWorkflowId = null;

    if (workflowFormEyebrow) {
        workflowFormEyebrow.textContent = "Create workflow";
    }

    if (workflowFormTitle) {
        workflowFormTitle.textContent = "Register a new workflow";
    }

    if (workflowFormDescription) {
        workflowFormDescription.textContent = "Capture the workflow details, then submit them directly to the active DAO-backed API.";
    }

    if (workflowSubmitButton) {
        workflowSubmitButton.textContent = "Add workflow";
    }

    if (workflowCancelButton) {
        workflowCancelButton.classList.add("hidden");
    }
}

function populateWorkflowForm(workflowId) {
    const workflow = workflowsById.get(workflowId);
    if (!workflow) {
        showStatus(`Workflow #${workflowId} could not be loaded for editing.`, true);
        return;
    }

    editingWorkflowId = workflowId;

    if (workflowIdField) {
        workflowIdField.value = String(workflowId);
    }

    if (workflowNameField) {
        workflowNameField.value = workflow.workflow_name || workflow.name || "";
        workflowNameField.focus();
    }

    if (workflowDescriptionField) {
        workflowDescriptionField.value = workflow.workflow_description || workflow.description || "";
    }

    if (workflowTypeField) {
        workflowTypeField.value = workflow.workflow_type || workflow.type || "";
    }

    if (workflowSubtypeField) {
        workflowSubtypeField.value = workflow.workflow_subtype || workflow.subtype || "";
    }

    if (workflowFormEyebrow) {
        workflowFormEyebrow.textContent = "Change workflow";
    }

    if (workflowFormTitle) {
        workflowFormTitle.textContent = `Update workflow #${workflowId}`;
    }

    if (workflowFormDescription) {
        workflowFormDescription.textContent = "Edit the non-ID workflow fields and save the changes back through the DAO-backed API.";
    }

    if (workflowSubmitButton) {
        workflowSubmitButton.textContent = "Save changes";
    }

    if (workflowCancelButton) {
        workflowCancelButton.classList.remove("hidden");
    }
}

function renderWorkflows(workflows) {
    if (!workflowTableBody) {
        return;
    }

    if (!Array.isArray(workflows) || workflows.length === 0) {
        workflowsById = new Map();
        workflowTableBody.innerHTML = emptyStateMarkup;
        return;
    }

    workflowsById = new Map(
        workflows
            .map((workflow) => [Number(workflow.workflow_id ?? workflow.id), workflow])
            .filter(([workflowId]) => !Number.isNaN(workflowId))
    );

    const rows = workflows.map((workflow) => {
        const workflowId = workflow.workflow_id ?? workflow.id ?? "N/A";
        const workflowName = workflow.workflow_name || workflow.name || "N/A";
        const workflowDescription = workflow.workflow_description || workflow.description || "N/A";
        const workflowType = workflow.workflow_type || workflow.type || "N/A";
        const workflowSubtype = workflow.workflow_subtype || workflow.subtype || "N/A";
        const createdBy = workflow.created_by || workflow.user || "System";

        return `
            <tr data-workflow-id="${workflowId}" class="transition hover:bg-slate-50">
                <td class="whitespace-nowrap px-4 py-4 font-medium text-slate-900">${escapeHtml(workflowId)}</td>
                <td class="px-4 py-4 text-slate-700">${escapeHtml(workflowName)}</td>
                <td class="max-w-xs px-4 py-4 text-slate-600">${escapeHtml(workflowDescription)}</td>
                <td class="px-4 py-4 text-slate-700">${escapeHtml(workflowType)}</td>
                <td class="px-4 py-4 text-slate-700">${escapeHtml(workflowSubtype)}</td>
                <td class="px-4 py-4 text-slate-500">${escapeHtml(createdBy)}</td>
                <td class="px-4 py-4 text-right">
                    <button
                        type="button"
                        class="change-workflow-button mr-2 inline-flex items-center justify-center rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-amber-700 transition hover:border-amber-300 hover:bg-amber-100"
                        data-workflow-id="${workflowId}"
                    >
                        Change
                    </button>
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
                <td colspan="7" class="px-4 py-10 text-center text-sm text-rose-600">Failed to load workflows.</td>
            </tr>
        `;
        showStatus(result.error_message || "Failed to load workflows.", true);
        return;
    }

    renderWorkflows(result.data);
}

function buildWorkflowPayload() {
    if (!workflowForm) {
        return null;
    }

    const formData = new FormData(workflowForm);
    const name = String(formData.get("name") || "").trim();
    const description = String(formData.get("description") || "").trim();
    const type = String(formData.get("type") || "").trim();
    const subtype = String(formData.get("subtype") || "").trim();

    if (!name || !type) {
        showStatus("Please enter both name and type.", true);
        return null;
    }

    return {
        name,
        description,
        type,
        subtype: subtype || "Standard",
        user: "AdminUser",
    };
}

async function addWorkflow(payload) {
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

    resetWorkflowForm();
    await loadWorkflows();
    showStatus("Workflow added successfully.");
}

async function updateWorkflow(workflowId, payload) {
    const result = await requestJson(
        `/api/workflows/${workflowId}`,
        {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        },
        "Failed to update workflow."
    );

    if (result.return_code !== 0) {
        showStatus(result.error_message || "Failed to update workflow.", true);
        return;
    }

    resetWorkflowForm();
    await loadWorkflows();
    showStatus(`Workflow #${workflowId} updated successfully.`);
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

            const payload = buildWorkflowPayload();
            if (!payload) {
                return;
            }

            if (editingWorkflowId === null) {
                await addWorkflow(payload);
                return;
            }

            await updateWorkflow(editingWorkflowId, payload);
        });
    }

    if (workflowCancelButton) {
        workflowCancelButton.addEventListener("click", () => {
            resetWorkflowForm();
            showStatus("Workflow edit cancelled.");
        });
    }

    if (workflowTableBody) {
        workflowTableBody.addEventListener("click", async (event) => {
            const changeButton = event.target.closest(".change-workflow-button");
            if (changeButton) {
                const workflowId = Number(changeButton.dataset.workflowId);
                if (!Number.isNaN(workflowId)) {
                    populateWorkflowForm(workflowId);
                }
                return;
            }

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
    if (!workflowForm || !workflowTableBody || !workflowSubmitButton) {
        return;
    }

    resetWorkflowForm();
    registerEventListeners();
    void loadWorkflows();
}

window.addEventListener("DOMContentLoaded", initializeWorkflowPage);