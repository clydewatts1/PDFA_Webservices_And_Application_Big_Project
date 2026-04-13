const sidebar = document.getElementById("sidebar");
const sidebarToggle = document.getElementById("sidebar-toggle");
const drawer = document.getElementById("entity-drawer");
const helpDrawer = document.getElementById("help-drawer");
const drawerOverlay = document.getElementById("drawer-overlay");
const drawerTitle = document.getElementById("drawer-title");
const drawerEyebrow = document.getElementById("drawer-eyebrow");
const helpDrawerTitle = document.getElementById("help-drawer-title");
const helpDrawerNote = document.getElementById("help-drawer-note");
const helpDrawerContent = document.getElementById("help-drawer-content");
const workflowForm = document.getElementById("workflow-drawer-form");
const roleForm = document.getElementById("role-drawer-form");
const guardForm = document.getElementById("guard-drawer-form");
const interactionForm = document.getElementById("interaction-drawer-form");
const interactionComponentForm = document.getElementById("interaction-component-drawer-form");
const workflowSubmit = document.getElementById("workflow-submit");
const roleSubmit = document.getElementById("role-submit");
const guardSubmit = document.getElementById("guard-submit");
const interactionSubmit = document.getElementById("interaction-submit");
const interactionComponentSubmit = document.getElementById("interaction-component-submit");
const workflowTableBody = document.getElementById("workflows-table-body");
const roleTableBody = document.getElementById("roles-table-body");
const guardTableBody = document.getElementById("guards-table-body");
const interactionTableBody = document.getElementById("interactions-table-body");
const interactionComponentTableBody = document.getElementById("interaction-components-table-body");
const ajaxToastHost = document.getElementById("ajax-toast-host");
let helpRequestId = 0;

function hideToasts() {
    const toasts = document.querySelectorAll("[data-toast]");
    if (!toasts.length) {
        return;
    }

    window.setTimeout(() => {
        toasts.forEach((toast) => {
            toast.hidden = true;
        });
    }, 4500);
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

/**
 * Set a button to loading state.
 * @param {HTMLElement} button
 * @returns {{button: HTMLElement, originalLabel: string}} State object for restoration.
 */
function setButtonLoading(button) {
    if (!button) {
        return {button, originalLabel: ""};
    }
    const originalLabel = button.textContent || "Save";
    button.disabled = true;
    button.textContent = "Saving...";
    return {button, originalLabel};
}

/**
 * Restore a button from loading state.
 * @param {Object} state - Object returned by setButtonLoading.
 */
function restoreButtonState(state) {
    if (state?.button) {
        state.button.disabled = false;
        state.button.textContent = state.originalLabel || "Save";
    }
}

/**
 * Execute API request with JSON payload and CSRF token.
 * @param {string} endpoint
 * @param {string} method
 * @param {Object} payload
 * @param {string} csrfToken
 * @returns {Promise<Object>} Parsed JSON response.
 */
async function executeApiRequest(endpoint, method, payload, csrfToken) {
    const response = await fetch(endpoint, {
        method,
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-CSRF-Token": csrfToken,
        },
        body: JSON.stringify(payload),
    });

    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(result.error || "Unable to save right now.");
    }
    return result;
}

/**
 * Validate API response contains expected ID field.
 * @param {Object} result - Response object.
 * @param {string} idField - Expected field name for the entity ID (e.g., 'workflow_id').
 * @param {string} action - Action name for error message.
 * @throws {Error} If ID field is missing or falsy.
 */
function validateApiResponse(result, idField, action) {
    if (!result[idField]) {
        throw new Error(`${action} succeeded but response payload was incomplete.`);
    }
}

function showAjaxToast(message, tone = "success") {
    if (!ajaxToastHost) {
        window.alert(message);
        return;
    }

    const toast = document.createElement("section");
    toast.dataset.toast = "";
    toast.className = [
        "pointer-events-auto rounded-google border bg-surface px-4 py-3 text-sm shadow-google transition",
        tone === "error" ? "border-danger/20 text-danger" : "border-primary/20 text-primary",
    ].join(" ");
    toast.textContent = message;
    ajaxToastHost.prepend(toast);
    hideToasts();
}

function buildWorkflowRow(workflow) {
    const workflowId = Number.parseInt(workflow.workflow_id, 10);
    const workflowName = escapeHtml(workflow.workflow_name || "");
    const workflowDescriptionRaw = workflow.workflow_description || "";
    const workflowDescription = workflowDescriptionRaw ? escapeHtml(workflowDescriptionRaw) : "-";
    const workflowType = escapeHtml(workflow.workflow_type || "");
    const workflowSubtype = workflow.workflow_subtype ? ` / ${escapeHtml(workflow.workflow_subtype)}` : "";
    const createdBy = escapeHtml(workflow.created_by || "System");
    const csrfToken = escapeHtml(workflowForm?.querySelector('input[name="csrf_token"]')?.value || "");

    return `
        <tr data-workflow-row-id="${workflowId}" class="group border-b border-divider/70 last:border-b-0">
            <td class="px-6 py-4 font-medium text-ink">${workflowName}</td>
            <td class="px-6 py-4 text-muted"><span class="clamp-2">${workflowDescription}</span></td>
            <td class="px-6 py-4 text-muted">${workflowType}${workflowSubtype}</td>
            <td class="px-6 py-4 text-muted">${createdBy}</td>
            <td class="px-6 py-4 text-right">
                <div class="inline-flex items-center gap-2 opacity-0 transition group-hover:opacity-100">
                    <button type="button" data-drawer-open="workflow" data-workflow-id="${workflowId}" data-workflow-name="${workflowName}" data-workflow-description="${escapeHtml(workflowDescriptionRaw)}" data-workflow-type="${workflowType}" data-workflow-subtype="${escapeHtml(workflow.workflow_subtype || "")}" class="inline-flex h-9 w-9 items-center justify-center rounded-full text-muted transition hover:bg-primary/10 hover:text-primary">
                        <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20h4l10-10-4-4L4 16v4Z" /><path d="m13 7 4 4" /></svg>
                    </button>
                    <form action="/dashboard/workflows/${workflowId}/delete" method="post" data-delete-form="workflow">
                        <input type="hidden" name="csrf_token" value="${csrfToken}">
                        <button type="submit" class="inline-flex h-9 w-9 items-center justify-center rounded-full text-muted transition hover:bg-red-50 hover:text-danger">
                            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18" /><path d="M8 6V4h8v2" /><path d="M19 6l-1 14H6L5 6" /></svg>
                        </button>
                    </form>
                </div>
            </td>
        </tr>
    `;
}

function upsertWorkflowRow(workflow, prepend = false) {
    if (!workflowTableBody || !workflow?.workflow_id) {
        return;
    }

    const rowMarkup = buildWorkflowRow(workflow);
    const template = document.createElement("template");
    template.innerHTML = rowMarkup.trim();
    const newRow = template.content.firstElementChild;
    if (!newRow) {
        return;
    }

    const existingRow = workflowTableBody.querySelector(`tr[data-workflow-row-id="${workflow.workflow_id}"]`);
    if (existingRow) {
        existingRow.replaceWith(newRow);
        return;
    }

    const emptyRow = workflowTableBody.querySelector("tr[data-workflow-empty-row]");
    if (emptyRow) {
        emptyRow.remove();
    }

    if (prepend) {
        workflowTableBody.prepend(newRow);
        return;
    }

    workflowTableBody.appendChild(newRow);
}

function buildRoleRow(role) {
    const roleId = Number.parseInt(role.role_id, 10);
    const roleName = escapeHtml(role.role_name || "");
    const roleDescriptionRaw = role.role_description || "";
    const roleDescription = roleDescriptionRaw ? escapeHtml(roleDescriptionRaw) : "-";
    const roleType = escapeHtml(role.role_type || "");
    const roleSubtype = role.role_subtype ? ` / ${escapeHtml(role.role_subtype)}` : "";
    const updatedAt = escapeHtml(role.updated_at || role.created_at || "-");
    const csrfToken = escapeHtml(roleForm?.querySelector('input[name="csrf_token"]')?.value || "");

    return `
        <tr data-role-row-id="${roleId}" class="group border-b border-divider/70 last:border-b-0">
            <td class="px-6 py-4 font-medium text-ink">${roleName}</td>
            <td class="px-6 py-4 text-muted"><span class="clamp-2">${roleDescription}</span></td>
            <td class="px-6 py-4 text-muted">${roleType}${roleSubtype}</td>
            <td class="px-6 py-4 text-muted">${updatedAt}</td>
            <td class="px-6 py-4 text-right">
                <div class="inline-flex items-center gap-2 opacity-0 transition group-hover:opacity-100">
                    <button type="button" data-drawer-open="role" data-role-id="${roleId}" data-role-name="${roleName}" data-role-description="${escapeHtml(roleDescriptionRaw)}" data-role-type="${roleType}" data-role-subtype="${escapeHtml(role.role_subtype || "")}" class="inline-flex h-9 w-9 items-center justify-center rounded-full text-muted transition hover:bg-primary/10 hover:text-primary">
                        <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20h4l10-10-4-4L4 16v4Z" /><path d="m13 7 4 4" /></svg>
                    </button>
                    <form action="/dashboard/roles/${roleId}/delete" method="post" data-delete-form="role">
                        <input type="hidden" name="csrf_token" value="${csrfToken}">
                        <button type="submit" class="inline-flex h-9 w-9 items-center justify-center rounded-full text-muted transition hover:bg-red-50 hover:text-danger">
                            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18" /><path d="M8 6V4h8v2" /><path d="M19 6l-1 14H6L5 6" /></svg>
                        </button>
                    </form>
                </div>
            </td>
        </tr>
    `;
}

function upsertRoleRow(role, prepend = false) {
    if (!roleTableBody || !role?.role_id) {
        return;
    }

    const rowMarkup = buildRoleRow(role);
    const template = document.createElement("template");
    template.innerHTML = rowMarkup.trim();
    const newRow = template.content.firstElementChild;
    if (!newRow) {
        return;
    }

    const existingRow = roleTableBody.querySelector(`tr[data-role-row-id="${role.role_id}"]`);
    if (existingRow) {
        existingRow.replaceWith(newRow);
        return;
    }

    const emptyRow = roleTableBody.querySelector("tr[data-role-empty-row]");
    if (emptyRow) {
        emptyRow.remove();
    }

    if (prepend) {
        roleTableBody.prepend(newRow);
        return;
    }

    roleTableBody.appendChild(newRow);
}

function buildGuardRow(guard) {
    const guardId = Number.parseInt(guard.guard_id, 10);
    const guardName = escapeHtml(guard.guard_name || "");
    const guardDescriptionRaw = guard.guard_description || "";
    const guardDescription = guardDescriptionRaw ? escapeHtml(guardDescriptionRaw) : "-";
    const guardType = escapeHtml(guard.guard_type || "");
    const guardSubtype = guard.guard_subtype ? ` / ${escapeHtml(guard.guard_subtype)}` : "";
    const updatedAt = escapeHtml(guard.updated_at || guard.created_at || "-");
    const csrfToken = escapeHtml(guardForm?.querySelector('input[name="csrf_token"]')?.value || "");

    return `
        <tr data-guard-row-id="${guardId}" class="group border-b border-divider/70 last:border-b-0">
            <td class="px-6 py-4 font-medium text-ink">${guardName}</td>
            <td class="px-6 py-4 text-muted"><span class="clamp-2">${guardDescription}</span></td>
            <td class="px-6 py-4 text-muted">${guardType}${guardSubtype}</td>
            <td class="px-6 py-4 text-muted">${updatedAt}</td>
            <td class="px-6 py-4 text-right">
                <div class="inline-flex items-center gap-2 opacity-0 transition group-hover:opacity-100">
                    <button type="button" data-drawer-open="guard" data-guard-id="${guardId}" data-guard-name="${guardName}" data-guard-description="${escapeHtml(guardDescriptionRaw)}" data-guard-type="${guardType}" data-guard-subtype="${escapeHtml(guard.guard_subtype || "")}" class="inline-flex h-9 w-9 items-center justify-center rounded-full text-muted transition hover:bg-primary/10 hover:text-primary">
                        <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20h4l10-10-4-4L4 16v4Z" /><path d="m13 7 4 4" /></svg>
                    </button>
                    <form action="/dashboard/guards/${guardId}/delete" method="post" data-delete-form="guard">
                        <input type="hidden" name="csrf_token" value="${csrfToken}">
                        <button type="submit" class="inline-flex h-9 w-9 items-center justify-center rounded-full text-muted transition hover:bg-red-50 hover:text-danger">
                            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18" /><path d="M8 6V4h8v2" /><path d="M19 6l-1 14H6L5 6" /></svg>
                        </button>
                    </form>
                </div>
            </td>
        </tr>
    `;
}

function upsertGuardRow(guard, prepend = false) {
    if (!guardTableBody || !guard?.guard_id) {
        return;
    }

    const rowMarkup = buildGuardRow(guard);
    const template = document.createElement("template");
    template.innerHTML = rowMarkup.trim();
    const newRow = template.content.firstElementChild;
    if (!newRow) {
        return;
    }

    const existingRow = guardTableBody.querySelector(`tr[data-guard-row-id="${guard.guard_id}"]`);
    if (existingRow) {
        existingRow.replaceWith(newRow);
        return;
    }

    const emptyRow = guardTableBody.querySelector("tr[data-guard-empty-row]");
    if (emptyRow) {
        emptyRow.remove();
    }

    if (prepend) {
        guardTableBody.prepend(newRow);
        return;
    }

    guardTableBody.appendChild(newRow);
}

function buildInteractionRow(interaction) {
    const interactionId = Number.parseInt(interaction.interaction_id, 10);
    const interactionName = escapeHtml(interaction.interaction_name || "");
    const workflowName = escapeHtml(interactionTableBody?.dataset.activeWorkflowName || "-");
    const updatedAt = escapeHtml(interaction.updated_at || interaction.created_at || "-");
    const csrfToken = escapeHtml(interactionForm?.querySelector('input[name="csrf_token"]')?.value || "");

    return `
        <tr data-interaction-row-id="${interactionId}" class="group border-b border-divider/70 last:border-b-0">
            <td class="px-6 py-4 font-medium text-ink">${interactionId}</td>
            <td class="px-6 py-4 text-muted">${interactionName}</td>
            <td class="px-6 py-4 text-muted">${workflowName}</td>
            <td class="px-6 py-4 text-muted">${updatedAt}</td>
            <td class="px-6 py-4 text-right">
                <div class="inline-flex items-center gap-2 opacity-0 transition group-hover:opacity-100">
                    <button type="button" data-drawer-open="interaction" data-interaction-id="${interactionId}" data-interaction-name="${interactionName}" class="inline-flex h-9 w-9 items-center justify-center rounded-full text-muted transition hover:bg-primary/10 hover:text-primary">
                        <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20h4l10-10-4-4L4 16v4Z" /><path d="m13 7 4 4" /></svg>
                    </button>
                    <form action="/dashboard/interactions/${interactionId}/delete" method="post" data-delete-form="interaction">
                        <input type="hidden" name="csrf_token" value="${csrfToken}">
                        <button type="submit" class="inline-flex h-9 w-9 items-center justify-center rounded-full text-muted transition hover:bg-red-50 hover:text-danger">
                            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18" /><path d="M8 6V4h8v2" /><path d="M19 6l-1 14H6L5 6" /></svg>
                        </button>
                    </form>
                </div>
            </td>
        </tr>
    `;
}

function upsertInteractionRow(interaction, prepend = false) {
    if (!interactionTableBody || !interaction?.interaction_id) {
        return;
    }

    const rowMarkup = buildInteractionRow(interaction);
    const template = document.createElement("template");
    template.innerHTML = rowMarkup.trim();
    const newRow = template.content.firstElementChild;
    if (!newRow) {
        return;
    }

    const existingRow = interactionTableBody.querySelector(
        `tr[data-interaction-row-id="${interaction.interaction_id}"]`,
    );
    if (existingRow) {
        existingRow.replaceWith(newRow);
        return;
    }

    const emptyRow = interactionTableBody.querySelector("tr[data-interaction-empty-row]");
    if (emptyRow) {
        emptyRow.remove();
    }

    if (prepend) {
        interactionTableBody.prepend(newRow);
        return;
    }

    interactionTableBody.appendChild(newRow);
}

function buildInteractionComponentRow(component) {
    const componentId = Number.parseInt(component.interaction_component_id, 10);
    const componentName = escapeHtml(component.interaction_component_name || "");
    const componentDescriptionRaw = component.interaction_component_description || "";
    const componentDescription = componentDescriptionRaw ? escapeHtml(componentDescriptionRaw) : "-";
    const componentType = escapeHtml(component.interaction_component_type || "");
    const componentSubtype = component.interaction_component_subtype
        ? ` / ${escapeHtml(component.interaction_component_subtype)}`
        : "";
    const interactionName = escapeHtml(component.interaction_name || "Unknown interaction");
    const roleName = escapeHtml(component.role_name || "No role");
    const guardName = escapeHtml(component.guard_name || "No guard");
    const directionLabel = escapeHtml(component.direction_label || component.direction || "-");
    const updatedAt = escapeHtml(component.updated_at || component.created_at || "-");
    const csrfToken = escapeHtml(
        interactionComponentForm?.querySelector('input[name="csrf_token"]')?.value || "",
    );
    const interactionId = escapeHtml(component.interaction_id || "");
    const roleId = escapeHtml(component.role_id || "");
    const guardId = escapeHtml(component.guard_id || "");
    const direction = escapeHtml(component.direction || "outbound");

    return `
        <tr data-interaction-component-row-id="${componentId}" class="group border-b border-divider/70 last:border-b-0">
            <td class="px-6 py-4">
                <div class="font-medium text-ink">${componentName}</div>
                <div class="mt-1 text-muted"><span class="clamp-2">${componentDescription}</span></div>
            </td>
            <td class="px-6 py-4 text-muted">${componentType}${componentSubtype}</td>
            <td class="px-6 py-4 text-muted">${interactionName}</td>
            <td class="px-6 py-4 text-muted">
                <div>${roleName}</div>
                <div class="mt-1 text-xs text-muted/80">${guardName}</div>
            </td>
            <td class="px-6 py-4 text-muted">${directionLabel}</td>
            <td class="px-6 py-4 text-muted">${updatedAt}</td>
            <td class="px-6 py-4 text-right">
                <div class="inline-flex items-center gap-2 opacity-0 transition group-hover:opacity-100">
                    <button type="button" data-drawer-open="interaction-component" data-interaction-component-id="${componentId}" data-interaction-component-name="${componentName}" data-interaction-component-description="${escapeHtml(componentDescriptionRaw)}" data-interaction-component-type="${componentType}" data-interaction-component-subtype="${escapeHtml(component.interaction_component_subtype || "")}" data-interaction-id="${interactionId}" data-role-id="${roleId}" data-guard-id="${guardId}" data-direction="${direction}" class="inline-flex h-9 w-9 items-center justify-center rounded-full text-muted transition hover:bg-primary/10 hover:text-primary">
                        <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 20h4l10-10-4-4L4 16v4Z" /><path d="m13 7 4 4" /></svg>
                    </button>
                    <form action="/dashboard/interaction-components/${componentId}/delete" method="post" data-delete-form="interaction component">
                        <input type="hidden" name="csrf_token" value="${csrfToken}">
                        <button type="submit" class="inline-flex h-9 w-9 items-center justify-center rounded-full text-muted transition hover:bg-red-50 hover:text-danger">
                            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18" /><path d="M8 6V4h8v2" /><path d="M19 6l-1 14H6L5 6" /></svg>
                        </button>
                    </form>
                </div>
            </td>
        </tr>
    `;
}

function upsertInteractionComponentRow(component, prepend = false) {
    if (!interactionComponentTableBody || !component?.interaction_component_id) {
        return;
    }

    const rowMarkup = buildInteractionComponentRow(component);
    const template = document.createElement("template");
    template.innerHTML = rowMarkup.trim();
    const newRow = template.content.firstElementChild;
    if (!newRow) {
        return;
    }

    const existingRow = interactionComponentTableBody.querySelector(
        `tr[data-interaction-component-row-id="${component.interaction_component_id}"]`,
    );
    if (existingRow) {
        existingRow.replaceWith(newRow);
        return;
    }

    const emptyRow = interactionComponentTableBody.querySelector("tr[data-interaction-component-empty-row]");
    if (emptyRow) {
        emptyRow.remove();
    }

    if (prepend) {
        interactionComponentTableBody.prepend(newRow);
        return;
    }

    interactionComponentTableBody.appendChild(newRow);
}

function bindWorkflowFormSubmission() {
    if (!workflowForm) {
        return;
    }

    workflowForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const workflowNameInput = document.getElementById("workflow_name");
        const workflowDescriptionInput = document.getElementById("workflow_description");
        const workflowTypeInput = document.getElementById("workflow_type");
        const workflowSubtypeInput = document.getElementById("workflow_subtype");
        const workflowIdInput = document.getElementById("workflow_id");
        const csrfTokenInput = workflowForm.querySelector('input[name="csrf_token"]');

        const workflowName = workflowNameInput?.value?.trim() || "";
        const workflowType = workflowTypeInput?.value?.trim() || "";
        if (!workflowName || !workflowType) {
            showAjaxToast("Workflow name and type are required.", "error");
            return;
        }

        const workflowId = workflowIdInput?.value?.trim() || "";
        const isUpdate = Boolean(workflowId);
        const csrfToken = csrfTokenInput?.value || "";
        const payload = {
            name: workflowName,
            description: workflowDescriptionInput?.value?.trim() || "",
            type: workflowType,
            subtype: workflowSubtypeInput?.value?.trim() || "Standard",
            csrf_token: csrfToken,
        };

        const endpoint = isUpdate ? `/api/workflows/${encodeURIComponent(workflowId)}` : "/api/workflows";
        const method = isUpdate ? "PUT" : "POST";
        const buttonState = setButtonLoading(workflowSubmit);

        try {
            const result = await executeApiRequest(endpoint, method, payload, csrfToken);
            validateApiResponse(result, "workflow_id", "Workflow save");

            upsertWorkflowRow(result, !isUpdate);
            closeEntityDrawer();
            showAjaxToast(
                isUpdate ? `Workflow #${result.workflow_id} updated.` : `Workflow #${result.workflow_id} created.`,
                "success",
            );
        } catch (error) {
            showAjaxToast(error.message || "Unable to save workflow.", "error");
        } finally {
            restoreButtonState(buttonState);
        }
    });
}

function bindRoleFormSubmission() {
    if (!roleForm) {
        return;
    }

    roleForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const roleNameInput = document.getElementById("role_name");
        const roleDescriptionInput = document.getElementById("role_description");
        const roleTypeInput = document.getElementById("role_type");
        const roleSubtypeInput = document.getElementById("role_subtype");
        const roleIdInput = document.getElementById("role_id");
        const csrfTokenInput = roleForm.querySelector('input[name="csrf_token"]');

        const roleName = roleNameInput?.value?.trim() || "";
        const roleType = roleTypeInput?.value?.trim() || "";
        if (!roleName || !roleType) {
            showAjaxToast("Role name and type are required.", "error");
            return;
        }

        const roleId = roleIdInput?.value?.trim() || "";
        const isUpdate = Boolean(roleId);
        const csrfToken = csrfTokenInput?.value || "";
        const payload = {
            name: roleName,
            description: roleDescriptionInput?.value?.trim() || "",
            type: roleType,
            subtype: roleSubtypeInput?.value?.trim() || "Standard",
            csrf_token: csrfToken,
        };

        const endpoint = isUpdate ? `/api/roles/${encodeURIComponent(roleId)}` : "/api/roles";
        const method = isUpdate ? "PUT" : "POST";
        const buttonState = setButtonLoading(roleSubmit);

        try {
            const result = await executeApiRequest(endpoint, method, payload, csrfToken);
            validateApiResponse(result, "role_id", "Role save");

            upsertRoleRow(result, !isUpdate);
            closeEntityDrawer();
            showAjaxToast(
                isUpdate ? `Role #${result.role_id} updated.` : `Role #${result.role_id} created.`,
                "success",
            );
        } catch (error) {
            showAjaxToast(error.message || "Unable to save role.", "error");
        } finally {
            restoreButtonState(buttonState);
        }
    });
}

function bindGuardFormSubmission() {
    if (!guardForm) {
        return;
    }

    guardForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const guardNameInput = document.getElementById("guard_name");
        const guardDescriptionInput = document.getElementById("guard_description");
        const guardTypeInput = document.getElementById("guard_type");
        const guardSubtypeInput = document.getElementById("guard_subtype");
        const guardIdInput = document.getElementById("guard_id");
        const csrfTokenInput = guardForm.querySelector('input[name="csrf_token"]');

        const guardName = guardNameInput?.value?.trim() || "";
        const guardType = guardTypeInput?.value?.trim() || "";
        if (!guardName || !guardType) {
            showAjaxToast("Guard name and type are required.", "error");
            return;
        }

        const guardId = guardIdInput?.value?.trim() || "";
        const isUpdate = Boolean(guardId);
        const csrfToken = csrfTokenInput?.value || "";
        const payload = {
            name: guardName,
            description: guardDescriptionInput?.value?.trim() || "",
            type: guardType,
            subtype: guardSubtypeInput?.value?.trim() || "Standard",
            csrf_token: csrfToken,
        };

        const endpoint = isUpdate ? `/api/guards/${encodeURIComponent(guardId)}` : "/api/guards";
        const method = isUpdate ? "PUT" : "POST";
        const buttonState = setButtonLoading(guardSubmit);

        try {
            const result = await executeApiRequest(endpoint, method, payload, csrfToken);
            validateApiResponse(result, "guard_id", "Guard save");

            upsertGuardRow(result, !isUpdate);
            closeEntityDrawer();
            showAjaxToast(
                isUpdate ? `Guard #${result.guard_id} updated.` : `Guard #${result.guard_id} created.`,
                "success",
            );
        } catch (error) {
            showAjaxToast(error.message || "Unable to save guard.", "error");
        } finally {
            restoreButtonState(buttonState);
        }
    });
}

function bindInteractionFormSubmission() {
    if (!interactionForm) {
        return;
    }

    interactionForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const interactionNameInput = document.getElementById("interaction_name");
        const interactionIdInput = document.getElementById("interaction_id_original");
        const csrfTokenInput = interactionForm.querySelector('input[name="csrf_token"]');

        const interactionName = interactionNameInput?.value?.trim() || "";
        if (!interactionName) {
            showAjaxToast("Interaction name is required.", "error");
            return;
        }

        const interactionId = interactionIdInput?.value?.trim() || "";
        const isUpdate = Boolean(interactionId);
        const csrfToken = csrfTokenInput?.value || "";
        const payload = {
            name: interactionName,
            csrf_token: csrfToken,
        };

        const endpoint = isUpdate ? `/api/interactions/${encodeURIComponent(interactionId)}` : "/api/interactions";
        const method = isUpdate ? "PUT" : "POST";
        const buttonState = setButtonLoading(interactionSubmit);

        try {
            const result = await executeApiRequest(endpoint, method, payload, csrfToken);
            validateApiResponse(result, "interaction_id", "Interaction save");

            upsertInteractionRow(result, !isUpdate);
            closeEntityDrawer();
            showAjaxToast(
                isUpdate
                    ? `Interaction #${result.interaction_id} updated.`
                    : `Interaction #${result.interaction_id} created.`,
                "success",
            );
        } catch (error) {
            showAjaxToast(error.message || "Unable to save interaction.", "error");
        } finally {
            restoreButtonState(buttonState);
        }
    });
}

function bindInteractionComponentFormSubmission() {
    if (!interactionComponentForm) {
        return;
    }

    interactionComponentForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const componentIdInput = document.getElementById("interaction_component_id");
        const componentNameInput = document.getElementById("interaction_component_name");
        const componentDescriptionInput = document.getElementById("interaction_component_description");
        const componentTypeInput = document.getElementById("interaction_component_type");
        const componentSubtypeInput = document.getElementById("interaction_component_subtype");
        const interactionIdInput = document.getElementById("component_interaction_id");
        const roleIdInput = document.getElementById("component_role_id");
        const guardIdInput = document.getElementById("component_guard_id");
        const directionInput = document.getElementById("component_direction");
        const csrfTokenInput = interactionComponentForm.querySelector('input[name="csrf_token"]');

        const componentName = componentNameInput?.value?.trim() || "";
        const componentType = componentTypeInput?.value?.trim() || "";
        const interactionId = interactionIdInput?.value?.trim() || "";
        if (!componentName || !componentType || !interactionId) {
            showAjaxToast("Component name, type, and interaction are required.", "error");
            return;
        }

        const componentId = componentIdInput?.value?.trim() || "";
        const isUpdate = Boolean(componentId);
        const csrfToken = csrfTokenInput?.value || "";
        const payload = {
            name: componentName,
            description: componentDescriptionInput?.value?.trim() || "",
            type: componentType,
            subtype: componentSubtypeInput?.value?.trim() || "",
            interaction_id: interactionId,
            role_id: roleIdInput?.value?.trim() || null,
            guard_id: guardIdInput?.value?.trim() || null,
            direction: directionInput?.value || "outbound",
            csrf_token: csrfToken,
        };

        const endpoint = isUpdate
            ? `/api/interaction-components/${encodeURIComponent(componentId)}`
            : "/api/interaction-components";
        const method = isUpdate ? "PUT" : "POST";
        const buttonState = setButtonLoading(interactionComponentSubmit);

        try {
            const result = await executeApiRequest(endpoint, method, payload, csrfToken);
            validateApiResponse(result, "interaction_component_id", "Interaction component save");

            upsertInteractionComponentRow(result, !isUpdate);
            closeEntityDrawer();
            showAjaxToast(
                isUpdate
                    ? `Interaction component #${result.interaction_component_id} updated.`
                    : `Interaction component #${result.interaction_component_id} created.`,
                "success",
            );
        } catch (error) {
            showAjaxToast(error.message || "Unable to save interaction component.", "error");
        } finally {
            restoreButtonState(buttonState);
        }
    });
}

function isEntityDrawerOpen() {
    return Boolean(drawer && !drawer.classList.contains("translate-x-full"));
}

function isHelpDrawerOpen() {
    return Boolean(helpDrawer && !helpDrawer.classList.contains("translate-x-full"));
}

function showOverlay() {
    if (!drawerOverlay) {
        return;
    }

    drawerOverlay.classList.remove("pointer-events-none", "opacity-0");
    drawerOverlay.classList.add("opacity-100");
}

function hideOverlayIfIdle() {
    if (!drawerOverlay || isEntityDrawerOpen() || isHelpDrawerOpen()) {
        return;
    }

    drawerOverlay.classList.add("pointer-events-none", "opacity-0");
    drawerOverlay.classList.remove("opacity-100");
}

function setSidebarOpen(isOpen) {
    if (!sidebar) {
        return;
    }

    sidebar.classList.toggle("-translate-x-full", !isOpen);
}

function resetWorkflowDrawer() {
    if (!workflowForm) {
        return;
    }

    workflowForm.reset();
    document.getElementById("workflow_id").value = "";
    drawerEyebrow.textContent = "Create workflow";
    drawerTitle.textContent = "Create workflow";
}

function resetRoleDrawer() {
    if (!roleForm) {
        return;
    }

    roleForm.reset();
    document.getElementById("role_id").value = "";
    drawerEyebrow.textContent = "Create role";
    drawerTitle.textContent = "Create role";
}

function resetGuardDrawer() {
    if (!guardForm) {
        return;
    }

    guardForm.reset();
    document.getElementById("guard_id").value = "";
    drawerEyebrow.textContent = "Create guard";
    drawerTitle.textContent = "Create guard";
}

function resetInteractionDrawer() {
    if (!interactionForm) {
        return;
    }

    interactionForm.reset();
    document.getElementById("interaction_id_original").value = "";
    drawerEyebrow.textContent = "Create interaction";
    drawerTitle.textContent = "Create interaction";
}

function resetInteractionComponentDrawer() {
    if (!interactionComponentForm) {
        return;
    }

    interactionComponentForm.reset();
    document.getElementById("interaction_component_id").value = "";
    document.getElementById("component_direction").value = "outbound";
    drawerEyebrow.textContent = "Create interaction component";
    drawerTitle.textContent = "Create interaction component";
}

function hideDrawerForms() {
    if (workflowForm) {
        workflowForm.classList.add("hidden");
    }
    if (roleForm) {
        roleForm.classList.add("hidden");
    }
    if (guardForm) {
        guardForm.classList.add("hidden");
    }
    if (interactionForm) {
        interactionForm.classList.add("hidden");
    }
    if (interactionComponentForm) {
        interactionComponentForm.classList.add("hidden");
    }
    if (workflowSubmit) {
        workflowSubmit.classList.add("hidden");
    }
    if (roleSubmit) {
        roleSubmit.classList.add("hidden");
    }
    if (guardSubmit) {
        guardSubmit.classList.add("hidden");
    }
    if (interactionSubmit) {
        interactionSubmit.classList.add("hidden");
    }
    if (interactionComponentSubmit) {
        interactionComponentSubmit.classList.add("hidden");
    }
}

function closeHelpDrawer() {
    if (!helpDrawer) {
        return;
    }

    helpDrawer.classList.add("translate-x-full");
    hideOverlayIfIdle();
}

function setHelpState(title, note, bodyHtml) {
    if (helpDrawerTitle) {
        helpDrawerTitle.textContent = title;
    }
    if (helpDrawerNote) {
        helpDrawerNote.textContent = note;
    }
    if (helpDrawerContent) {
        helpDrawerContent.innerHTML = bodyHtml;
    }
}

function prettifyTopic(topic) {
    if (!topic) {
        return "help";
    }

    return topic
        .replace(/^context-/, "")
        .replace(/-/g, " ")
        .trim();
}

async function openHelpDrawer(topic) {
    if (!helpDrawer) {
        return;
    }

    closeEntityDrawer();
    helpDrawer.classList.remove("translate-x-full");
    showOverlay();

    const requestTopic = topic || "index";
    const activeRequestId = ++helpRequestId;
    setHelpState("Loading help", `Loading help for ${prettifyTopic(requestTopic)}.`, "<p>Loading help content...</p>");

    try {
        const response = await fetch(`/help/${encodeURIComponent(requestTopic)}`, {
            headers: { Accept: "application/json" },
        });
        const payload = await response.json();

        if (activeRequestId !== helpRequestId) {
            return;
        }

        if (!response.ok) {
            throw new Error(payload.error || "Unable to load help content.");
        }

        const note = payload.fallback && payload.topic !== payload.resolved_topic
            ? `No specific help was found for ${prettifyTopic(payload.topic)}. Showing the default help index instead.`
            : `Showing help for ${prettifyTopic(payload.resolved_topic)}.`;
        setHelpState(payload.title || "Help", note, payload.html || "<p>No help content available.</p>");
    } catch (error) {
        if (activeRequestId !== helpRequestId) {
            return;
        }

        setHelpState(
            "Help unavailable",
            "The help panel could not load content for this section.",
            `<p>${error.message}</p>`,
        );
    }
}

function openDrawer(kind, dataset = {}) {
    if (!drawer || !drawerOverlay) {
        return;
    }

    closeHelpDrawer();
    hideDrawerForms();
    if (kind === "workflow" && workflowForm) {
        workflowForm.classList.remove("hidden");
        workflowSubmit.classList.remove("hidden");
        resetWorkflowDrawer();
        if (dataset.workflowId) {
            drawerEyebrow.textContent = "Update workflow";
            drawerTitle.textContent = `Edit workflow #${dataset.workflowId}`;
            document.getElementById("workflow_id").value = dataset.workflowId || "";
            document.getElementById("workflow_name").value = dataset.workflowName || "";
            document.getElementById("workflow_description").value = dataset.workflowDescription || "";
            document.getElementById("workflow_type").value = dataset.workflowType || "";
            document.getElementById("workflow_subtype").value = dataset.workflowSubtype || "";
        }
    }

    if (kind === "role" && roleForm) {
        roleForm.classList.remove("hidden");
        roleSubmit.classList.remove("hidden");
        resetRoleDrawer();
        if (dataset.roleId) {
            drawerEyebrow.textContent = "Update role";
            drawerTitle.textContent = `Edit role #${dataset.roleId}`;
            document.getElementById("role_id").value = dataset.roleId || "";
            document.getElementById("role_name").value = dataset.roleName || "";
            document.getElementById("role_description").value = dataset.roleDescription || "";
            document.getElementById("role_type").value = dataset.roleType || "";
            document.getElementById("role_subtype").value = dataset.roleSubtype || "";
        }
    }

    if (kind === "guard" && guardForm) {
        guardForm.classList.remove("hidden");
        guardSubmit.classList.remove("hidden");
        resetGuardDrawer();
        if (dataset.guardId) {
            drawerEyebrow.textContent = "Update guard";
            drawerTitle.textContent = `Edit guard #${dataset.guardId}`;
            document.getElementById("guard_id").value = dataset.guardId || "";
            document.getElementById("guard_name").value = dataset.guardName || "";
            document.getElementById("guard_description").value = dataset.guardDescription || "";
            document.getElementById("guard_type").value = dataset.guardType || "";
            document.getElementById("guard_subtype").value = dataset.guardSubtype || "";
        }
    }

    if (kind === "interaction" && interactionForm) {
        interactionForm.classList.remove("hidden");
        interactionSubmit.classList.remove("hidden");
        resetInteractionDrawer();
        if (dataset.interactionId) {
            drawerEyebrow.textContent = "Update interaction";
            drawerTitle.textContent = `Edit interaction #${dataset.interactionId}`;
            document.getElementById("interaction_id_original").value = dataset.interactionId || "";
            document.getElementById("interaction_name").value = dataset.interactionName || "";
        }
    }

    if (kind === "interaction-component" && interactionComponentForm) {
        interactionComponentForm.classList.remove("hidden");
        interactionComponentSubmit.classList.remove("hidden");
        resetInteractionComponentDrawer();
        if (dataset.interactionComponentId) {
            drawerEyebrow.textContent = "Update interaction component";
            drawerTitle.textContent = `Edit interaction component #${dataset.interactionComponentId}`;
            document.getElementById("interaction_component_id").value = dataset.interactionComponentId || "";
            document.getElementById("interaction_component_name").value = dataset.interactionComponentName || "";
            document.getElementById("interaction_component_description").value = dataset.interactionComponentDescription || "";
            document.getElementById("interaction_component_type").value = dataset.interactionComponentType || "";
            document.getElementById("interaction_component_subtype").value = dataset.interactionComponentSubtype || "";
            document.getElementById("component_interaction_id").value = dataset.interactionId || "";
            document.getElementById("component_role_id").value = dataset.roleId || "";
            document.getElementById("component_guard_id").value = dataset.guardId || "";
            document.getElementById("component_direction").value = dataset.direction || "outbound";
        }
    }

    drawer.classList.remove("translate-x-full");
    showOverlay();
}

function closeEntityDrawer() {
    if (!drawer || !drawerOverlay) {
        return;
    }

    drawer.classList.add("translate-x-full");
    resetWorkflowDrawer();
    resetRoleDrawer();
    resetGuardDrawer();
    resetInteractionDrawer();
    resetInteractionComponentDrawer();
    hideDrawerForms();
    hideOverlayIfIdle();
}

function closeAllPanels() {
    closeEntityDrawer();
    closeHelpDrawer();
}

function bindDrawerTriggers() {
    document.addEventListener("click", (event) => {
        if (!(event.target instanceof Element)) {
            return;
        }

        const drawerOpenTrigger = event.target.closest("[data-drawer-open]");
        if (drawerOpenTrigger) {
            openDrawer(drawerOpenTrigger.dataset.drawerOpen, drawerOpenTrigger.dataset);
            return;
        }

        const drawerCloseTrigger = event.target.closest("[data-drawer-close]");
        if (drawerCloseTrigger) {
            closeEntityDrawer();
            return;
        }

        const helpOpenTrigger = event.target.closest("[data-help-open]");
        if (helpOpenTrigger) {
            openHelpDrawer(helpOpenTrigger.dataset.helpTopic || "index");
            return;
        }

        const helpCloseTrigger = event.target.closest("[data-help-close]");
        if (helpCloseTrigger) {
            closeHelpDrawer();
        }
    });

    if (drawerOverlay) {
        drawerOverlay.addEventListener("click", closeAllPanels);
    }
}

function bindDeleteConfirmations() {
    document.addEventListener("submit", (event) => {
        const submittedForm = event.target;
        if (!(submittedForm instanceof HTMLFormElement)) {
            return;
        }
        if (!submittedForm.matches("[data-delete-form]")) {
            return;
        }

        const entity = submittedForm.dataset.deleteForm || "record";
        const confirmed = window.confirm(`Delete this ${entity}?`);
        if (!confirmed) {
            event.preventDefault();
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    hideToasts();
    bindDrawerTriggers();
    bindDeleteConfirmations();
    bindWorkflowFormSubmission();
    bindRoleFormSubmission();
    bindGuardFormSubmission();
    bindInteractionFormSubmission();
    bindInteractionComponentFormSubmission();
    setSidebarOpen(window.innerWidth >= 768);

    if (sidebarToggle) {
        sidebarToggle.addEventListener("click", () => {
            const isHidden = sidebar?.classList.contains("-translate-x-full");
            setSidebarOpen(isHidden);
        });
    }
});