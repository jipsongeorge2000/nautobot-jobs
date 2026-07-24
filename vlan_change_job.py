"""
====================================================
Bulk VLAN Change Automation

Nautobot 2.4 Compatible

Features:
- Multiple ports
- Different VLAN per port
- Trunk protection
- Audit logging

====================================================
"""

from nautobot.apps.jobs import (
    Job,
    ObjectVar,
    TextVar,
    register_jobs,
)

from nautobot.dcim.models import Device


class BulkVlanChange(Job):


    class Meta:

        name = (
            "Bulk VLAN Change - Trunk Protected"
        )

        description = (
            "Change multiple ports with different VLANs safely"
        )


    device = ObjectVar(
        model=Device,
        description="Select Switch"
    )


    vlan_mapping = TextVar(
        description=(
            "Enter one per line: interface,vlan"
        )
    )


    def run(
        self,
        device,
        vlan_mapping,
    ):


        self.logger.info(
            "========== BULK VLAN CHANGE =========="
        )


        self.logger.info(
            f"Device: {device.name}"
        )



        changes = []


        for line in vlan_mapping.splitlines():

            if not line.strip():
                continue


            port, vlan = line.split(",")


            changes.append(
                {
                    "port": port.strip(),
                    "vlan": vlan.strip()
                }
            )



        self.logger.info(
            f"Total changes requested: {len(changes)}"
        )



        for change in changes:


            port = change["port"]

            vlan = change["vlan"]


            self.logger.info(
                "--------------------------------"
            )


            self.logger.info(
                f"Checking {port}"
            )


            #
            # Phase-1:
            # Nautobot validation
            #
            # Phase-2:
            # replace with live switch:
            #
            # show running interface port
            #


            if any(
                x in port.lower()
                for x in [
                    "po",
                    "port-channel"
                ]
            ):

                self.logger.warning(
                    f"{port} skipped - trunk/uplink detected"
                )

                continue



            self.logger.success(
                f"""
APPROVED CHANGE

Interface:
{port}

New VLAN:
{vlan}

"""
            )



        self.logger.success(
            "Bulk VLAN validation completed"
        )



register_jobs(
    BulkVlanChange
)


# =====================================================
# REGISTER JOB
# PHASE 39A-29D.6
# =====================================================

from nautobot.apps.jobs import register_jobs

register_jobs(
    BulkVlanChange
)

