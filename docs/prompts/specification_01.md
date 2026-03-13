The following tables are specified.



Control Columns
---------------

Each table has these control table

EffFromDateTime: Effective Start Date
EffToDateTime: Effective End Date 
DeleteInd: A active , D Deleted
InsertUserName:
UpdateUserName: 

Each table below will have a current table , and a history table.
The current table will hold the current record , and the history will contain the current record , and previous versions using snapshots - scd
The tracked or snapshot table will be suffixed with _Hist

Table: Workflow
----------------
Worflow table 
WorkflowName  : Primary Key, This is the short name of the workflow , example : CREDIT_VALIDATION
WorkflowDescription : Description of the Workflow , markdown format
WorkflowContextDescription: This is ai version of the workflow description
WorkflowStateInd: State Indicator A Active , I Inactive etc

Role
----

Roles: Assigning responsibilities to specific participants or automated agents.


RoleName: Primary Key , this is a short name for the role
WorkflowName: Foreign Key to Workflow
RoleDescription: This is a human readable description
RoleContextDescription: A AI friendly version of the description 
RoleConfiguration: Varchar or json , contains info on role
RoleConfigurationDescription: Human configuration  description in Markdown
RoleConfigurationContextDescription: A AI friendly version of the configuration description

Interaction
-----------

The communication patterns between components or roles.

InteractionName: Primary Key , this is a short name for the interaction
WorkflowName: Foreign Key to Workflow,Primary Key
InteractionDescription: A description of the interaction
InteractionContextDescription: AI description of the interaction
InteractionType: The interaction type. INTERACTION - generally interactions are dumb

Guard
-----

GuardName: Primary Key , the name of the guard
WorkflowName: Foreign Key to Workflow,Primary Key
GuardDescription: A description of guard for human
GuardContextDescription: AI context version of guard
GuardType: Type of Guard , DUMP , STANDARD
GuardConfiguration: The configuration of the guard in JSON format 

InteractionComponent
---------------------

InteractionComponentName: Primary Key
WorkflowName: Foreign Key to Workflow,Primary Key
InteractionComponentRelationShip: The direction and object , see below
InteractionComponentDescription
InteractionComponentContextDescription
SourceName
TargetName


UnitOfWork
---------
Defined as the discrete activities or tasks within the process.

UnitOfWorkID
UnitOfWorkType
UnitOfWorkPayLoad


Instance
--------

This is a running instance of the workflow

InstanceName: Primary Key 
WorkflowName: Workflow Name
InstanceDescription: 
InstanceContextDescription: 
InstanceState: Instance State A - Active , I Inactive , P - Paused
InstanceStateDate
InstanceStartDate
InstanceEndDate

Instanciation
-------------

The Role , Interaction , Interaction Component , Guard tables are replicated when an instance
is created with naming convention of adding instance name to the table. 




Definitions
-----------
Units of Work: Defined as the discrete activities or tasks within the process.
Interactions: The communication patterns between components or roles.
Guards: Logical conditions (often in the context of Petri nets or reactive objects) that must be met for a transition or interaction to occur.
Roles: Assigning responsibilities to specific participants or automated agents.
Interaction Components: Part of their work on software connectors and taxonomies, where they treat interaction as a first-class citizen in the architecture. 
InterSystems
InterSystems
 


Agostini, Alessandra. Simple Workflow Models.
---------------------------------------------

While a workflow model based on roles, interactions, guards, and units of work shares structural logic with Petri nets, it is not a Petri net by definition. Instead, these are the core components of the Balboa framework and the Software Process Data Analysis research pioneered by Alexander L. Wolf and Jonathan E. Cook in the late 1990s. 


Core Architectural Concepts in Balboa
--------------------------------------
The framework was designed around the specific entities you mentioned to handle the "noise" and complexity of real-world software development:
Events/Interactions: Balboa treats a process as a stream of discrete events. An interaction is a specific type of event where two or more entities (roles or components) communicate.
Units of Work: These are logical groupings of events. The framework helps identify where one "task" ends and another begins by analyzing the sequence of events.
Roles: Balboa allows for the registration of user-defined attributes, which include the roles (e.g., developer, tester, manager) associated with specific events or event collections.
Guards: While more common in the underlying Petri net or Finite State Machine (FSM) models that Balboa generates, guards represent the logic discovered by the framework that dictates whether a transition between two units of work is valid