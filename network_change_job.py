"""
====================================================
Network Change Jobs

Nautobot 3.0 Compatible

Canonical copy -- consolidated 2026-07-24 (TODO-020/028). Four
duplicate, unregistered copies of these classes existed elsewhere in
this JOBS_ROOT (network_change.py, jobs.py, local_jobs/jobs/jobs.py,
network_change/jobs.py) -- all quarantined to /opt/_to_be_deleted/,
this is the one real copy going forward.

version = "1.1.0"
  1.0.0 -- original two jobs, registered via the legacy module-level
           `jobs = [...]` list. That convention is silently ignored by
           this Nautobot version (3.0.10) -- confirmed neither job was
           actually discoverable via /api/extras/jobs/. Only
           vlan_change_job.py's classes showed up, because that file
           uses the modern `register_jobs()` call.
  1.1.0 -- switched to register_jobs() (matches vlan_change_job.py's
           working pattern), fixed platform-core/app/services/
           execution_engine.py's job class_path, which pointed at a
           module ("network_actions") that has never existed under
           this JOBS_ROOT.

Rollback: dry_run/execute/rollback and failover/check_interface/
raise_ticket are STUBS -- self.log_info(...) only, no real device
connection is made in any mode (confirmed: no netmiko/napalm/ssh/http
call anywhere below). This is consistent with the platform-wide
disclosed limitation that real device execution is not wired up
(execution mode is READ_ONLY -- see platform-core's
ai_control/autonomy_config.json). There is therefore no real rollback
procedure to document yet: "rollback" mode just logs the rollback
config text the same way "execute" logs the forward config, neither
is applied to a device. Document this honestly rather than describe a
rollback procedure that doesn't exist.

Input validation: StringVar fields are unvalidated free text (no
schema constraints beyond "some string was submitted") -- device_name
is checked against Device.objects (fails cleanly with log_failure if
not found); config/rollback/mode and action are not validated against
any schema before being logged.

Integration test suite against a lab device: not present, and not
buildable in this environment -- there is no lab device reachable
from this host to test against (see project_execution_mode_architecture
memory: device exec is stubbed platform-wide, not just here).
====================================================
"""

from nautobot.apps.jobs import Job, StringVar, register_jobs
from nautobot.dcim.models import Device


class NetworkChangeJob(Job):

    device_name = StringVar(description="Device name")
    config = StringVar(description="Configuration to apply")
    rollback = StringVar(description="Rollback configuration")
    mode = StringVar(description="Mode: dry_run / execute / rollback")

    class Meta:
        name = "Network Change Job"
        description = "Execute config with dry-run / execute / rollback"

    def run(self, data, commit):

        device_name = data.get("device_name")
        config = data.get("config")
        rollback = data.get("rollback")
        mode = data.get("mode")

        try:
            device = Device.objects.get(name=device_name)
        except Device.DoesNotExist:
            self.log_failure(f"Device {device_name} not found")
            return

        self.log_info(f"Mode: {mode}")
        self.log_info(f"Device: {device.name}")

        if mode == "dry_run":
            self.log_info(config)

        elif mode == "execute":
            self.log_info(config)

        elif mode == "rollback":
            self.log_info(rollback)

        else:
            self.log_failure("Invalid mode")
            return

        self.log_success("Completed")


class NetworkAction(Job):

    device = StringVar(description="Target device")
    action = StringVar(description="Action: failover / check_interface / raise_ticket")

    class Meta:
        name = "AIOps Network Action"
        description = "Triggered by platform-core decision engine"

    def run(self, data, commit):

        device_name = data.get("device")
        action = data.get("action")

        self.log_info(f"AIOps Action: {action}")
        self.log_info(f"Device: {device_name}")

        try:
            device = Device.objects.get(name=device_name)
        except Device.DoesNotExist:
            self.log_failure(f"Device {device_name} not found")
            return

        if action == "failover":
            result = f"Failover executed for {device.name}"

        elif action == "check_interface":
            result = f"Interface check completed for {device.name}"

        elif action == "raise_ticket":
            result = f"Ticket created for {device.name}"

        else:
            self.log_failure(f"Unknown action: {action}")
            return

        self.log_success(result)
        return result


register_jobs(
    NetworkChangeJob,
    NetworkAction,
)
