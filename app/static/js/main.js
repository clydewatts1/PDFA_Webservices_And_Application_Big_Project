const sidebar = document.getElementById("sidebar");
const sidebarToggle = document.getElementById("sidebar-toggle");
const drawer = document.getElementById("entity-drawer");
const drawerOverlay = document.getElementById("drawer-overlay");
const drawerTitle = document.getElementById("drawer-title");
const drawerEyebrow = document.getElementById("drawer-eyebrow");
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
    const interactionIdField = document.getElementById("interaction_id");
    interactionIdField.readOnly = false;
    interactionIdField.classList.remove("bg-canvas");
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

function openDrawer(kind, dataset = {}) {
    if (!drawer || !drawerOverlay) {
        return;
    }

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
            const interactionIdField = document.getElementById("interaction_id");
            interactionIdField.value = dataset.interactionId || "";
            interactionIdField.readOnly = true;
            interactionIdField.classList.add("bg-canvas");
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
    drawerOverlay.classList.remove("pointer-events-none", "opacity-0");
    drawerOverlay.classList.add("opacity-100");
}

function closeDrawer() {
    if (!drawer || !drawerOverlay) {
        return;
    }

    drawer.classList.add("translate-x-full");
    drawerOverlay.classList.add("pointer-events-none", "opacity-0");
    resetWorkflowDrawer();
    resetRoleDrawer();
    resetGuardDrawer();
    resetInteractionDrawer();
    resetInteractionComponentDrawer();
    hideDrawerForms();
}

function bindDrawerTriggers() {
    document.querySelectorAll("[data-drawer-open]").forEach((trigger) => {
        trigger.addEventListener("click", () => {
            openDrawer(trigger.dataset.drawerOpen, trigger.dataset);
        });
    });

    document.querySelectorAll("[data-drawer-close]").forEach((trigger) => {
        trigger.addEventListener("click", closeDrawer);
    });

    if (drawerOverlay) {
        drawerOverlay.addEventListener("click", closeDrawer);
    }
}

function bindDeleteConfirmations() {
    document.querySelectorAll("[data-delete-form]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const entity = form.dataset.deleteForm || "record";
            const confirmed = window.confirm(`Delete this ${entity}?`);
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    hideToasts();
    bindDrawerTriggers();
    bindDeleteConfirmations();
    setSidebarOpen(window.innerWidth >= 768);

    if (sidebarToggle) {
        sidebarToggle.addEventListener("click", () => {
            const isHidden = sidebar?.classList.contains("-translate-x-full");
            setSidebarOpen(isHidden);
        });
    }
});