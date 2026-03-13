# Data Model: Workflow Interaction Schema Foundation

## Global Control Columns
All current/history tables include:
- `EffFromDateTime` (required)
- `EffToDateTime` (nullable until closed)
- `DeleteInd` (`A` active, `D` deleted)
- `InsertUserName` (required)
- `UpdateUserName` (required)

Temporal invariant:
- Exactly one active current row exists per business key.
- On update, prior active row is closed by setting `EffToDateTime` before the replacement row is activated.

## Entity Definitions

### 1) Workflow
- Business key: `WorkflowName` (global unique)
- Fields: `WorkflowDescription`, `WorkflowContextDescription`, `WorkflowStateInd`
- Tables: `Workflow` (current), `Workflow_Hist` (history)

### 2) Role
- Business key: composite (`RoleName`, `WorkflowName`)
- Foreign key: `WorkflowName -> Workflow.WorkflowName`
- Fields: `RoleDescription`, `RoleContextDescription`, `RoleConfiguration`, `RoleConfigurationDescription`, `RoleConfigurationContextDescription`
- Tables: `Role`, `Role_Hist`

### 3) Interaction
- Business key: composite (`InteractionName`, `WorkflowName`)
- Foreign key: `WorkflowName -> Workflow.WorkflowName`
- Fields: `InteractionDescription`, `InteractionContextDescription`, `InteractionType`
- Tables: `Interaction`, `Interaction_Hist`

### 4) Guard
- Business key: composite (`GuardName`, `WorkflowName`)
- Foreign key: `WorkflowName -> Workflow.WorkflowName`
- Fields: `GuardDescription`, `GuardContextDescription`, `GuardType`, `GuardConfiguration`
- Tables: `Guard`, `Guard_Hist`

### 5) InteractionComponent
- Business key: composite (`InteractionComponentName`, `WorkflowName`)
- Foreign key: `WorkflowName -> Workflow.WorkflowName`
- Fields: `InteractionComponentRelationShip`, `InteractionComponentDescription`, `InteractionComponentContextDescription`, `SourceName`, `TargetName`
- Tables: `InteractionComponent`, `InteractionComponent_Hist`

### 6) UnitOfWork
- Business key: `UnitOfWorkID`
- Fields: `UnitOfWorkType`, `UnitOfWorkPayLoad`
- Tables: `UnitOfWork`, `UnitOfWork_Hist`

### 7) Instance
- Business key: `InstanceName` (global unique)
- Foreign key: `WorkflowName -> Workflow.WorkflowName`
- Fields: `InstanceDescription`, `InstanceContextDescription`, `InstanceState`, `InstanceStateDate`, `InstanceStartDate`, `InstanceEndDate`
- Tables: `Instance`, `Instance_Hist`

## Relationships
- Workflow 1 -> N Role
- Workflow 1 -> N Interaction
- Workflow 1 -> N Guard
- Workflow 1 -> N InteractionComponent
- Workflow 1 -> N Instance

Instantiation behavior:
- On `Instance` creation, baseline copies of Role/Interaction/Guard/InteractionComponent are replicated as instance-scoped rows in fixed tables (no runtime table creation).

## Validation Rules
- `EffToDateTime` must be greater than or equal to `EffFromDateTime`.
- Dependent entities must reference an existing active workflow.
- Duplicate business keys in active-current rows are rejected.
- `DeleteInd` allowed values: `A`, `D`.
- `InstanceState` allowed values for this increment: `A`, `I`, `P`.
