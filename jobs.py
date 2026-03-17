from nautobot.apps.jobs import Job, register_jobs
import subprocess


class RunAnsiblePlaybook(Job):

    class Meta:
        name = "Run Ansible Playbook"
        description = "Execute an Ansible playbook"

    def run(self):
        result = subprocess.run(
            ["ansible-playbook", "/opt/playbooks/test.yml"],
            capture_output=True,
            text=True,
        )

        self.logger.info(result.stdout)

        if result.returncode != 0:
            self.logger.error(result.stderr)
            raise Exception("Ansible playbook failed")


register_jobs(RunAnsiblePlaybook)
