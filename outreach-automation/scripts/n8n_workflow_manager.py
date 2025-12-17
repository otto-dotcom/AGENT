"""
n8n Workflow Manager for Outreach Automation System

This module provides connectivity to n8n instance for managing and executing
workflows for the automated outreach campaigns.
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
import time


class N8nWorkflowManager:
    """Manage n8n workflows for outreach campaigns."""

    def __init__(self, config_path: str = "config/mcp_config.json"):
        """Initialize the n8n workflow manager.

        Args:
            config_path: Path to MCP configuration file
        """
        self.config = self._load_config(config_path)
        self.api_url = os.getenv("N8N_API_URL", self.config["n8n"]["instance_url"])
        self.api_key = os.getenv("N8N_API_KEY")

        if not self.api_key:
            raise ValueError("N8N_API_KEY must be set in environment")

        # Remove trailing slash from URL
        self.api_url = self.api_url.rstrip("/")

    def _load_config(self, config_path: str) -> Dict:
        """Load MCP configuration."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def _make_request(self, method: str, endpoint: str,
                     data: Optional[Dict] = None,
                     params: Optional[Dict] = None) -> Dict:
        """Make authenticated request to n8n API.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint
            data: Request payload
            params: Query parameters

        Returns:
            API response as dictionary
        """
        headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        url = f"{self.api_url}/api/v1/{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PATCH":
                response = requests.patch(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ n8n API request failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise

    def list_workflows(self) -> List[Dict]:
        """List all workflows in the n8n instance.

        Returns:
            List of workflow objects
        """
        return self._make_request("GET", "workflows")

    def get_workflow(self, workflow_id: str) -> Dict:
        """Get details of a specific workflow.

        Args:
            workflow_id: n8n workflow ID

        Returns:
            Workflow object
        """
        return self._make_request("GET", f"workflows/{workflow_id}")

    def get_workflow_by_name(self, workflow_name: str) -> Optional[Dict]:
        """Find a workflow by its name.

        Args:
            workflow_name: Name of the workflow

        Returns:
            Workflow object or None if not found
        """
        workflows = self.list_workflows()
        for workflow in workflows:
            if workflow.get("name") == workflow_name:
                return workflow
        return None

    def execute_workflow(self, workflow_id: str, data: Optional[Dict] = None) -> Dict:
        """Execute a workflow.

        Args:
            workflow_id: n8n workflow ID
            data: Input data for the workflow

        Returns:
            Execution result
        """
        endpoint = f"workflows/{workflow_id}/execute"
        payload = {"data": data} if data else {}

        return self._make_request("POST", endpoint, payload)

    def trigger_workflow_webhook(self, workflow_id: str, data: Dict) -> Dict:
        """Trigger a workflow via webhook.

        Args:
            workflow_id: n8n workflow ID
            data: Webhook payload

        Returns:
            Webhook response
        """
        # Construct webhook URL
        webhook_url = f"{self.api_url}/webhook/{workflow_id}"

        headers = {"Content-Type": "application/json"}

        response = requests.post(webhook_url, json=data, headers=headers)
        response.raise_for_status()

        return response.json()

    def get_execution(self, execution_id: str) -> Dict:
        """Get details of a workflow execution.

        Args:
            execution_id: Execution ID

        Returns:
            Execution details
        """
        return self._make_request("GET", f"executions/{execution_id}")

    def get_executions(self, workflow_id: Optional[str] = None,
                       limit: int = 20) -> List[Dict]:
        """Get recent workflow executions.

        Args:
            workflow_id: Optional workflow ID to filter by
            limit: Maximum number of executions to return

        Returns:
            List of executions
        """
        params = {"limit": limit}
        if workflow_id:
            params["workflowId"] = workflow_id

        return self._make_request("GET", "executions", params=params)

    def wait_for_execution(self, execution_id: str,
                          timeout: int = 300,
                          poll_interval: int = 5) -> Dict:
        """Wait for a workflow execution to complete.

        Args:
            execution_id: Execution ID to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds

        Returns:
            Final execution status

        Raises:
            TimeoutError: If execution doesn't complete within timeout
        """
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(
                    f"Execution {execution_id} did not complete within {timeout}s"
                )

            execution = self.get_execution(execution_id)
            status = execution.get("status")

            if status in ["success", "error", "crashed"]:
                return execution

            time.sleep(poll_interval)

    def run_lead_enrichment(self, lead_data: List[Dict]) -> Dict:
        """Run the lead enrichment workflow.

        Args:
            lead_data: List of leads to enrich

        Returns:
            Execution result
        """
        workflow_config = self.config["n8n"]["workflows"]["lead_enrichment"]
        workflow = self.get_workflow_by_name(workflow_config["name"])

        if not workflow:
            raise ValueError(f"Workflow '{workflow_config['name']}' not found")

        return self.execute_workflow(workflow["id"], {"leads": lead_data})

    def run_email_campaign(self, campaign_data: Dict) -> Dict:
        """Run the email campaign workflow.

        Args:
            campaign_data: Campaign configuration and lead data

        Returns:
            Execution result
        """
        workflow_config = self.config["n8n"]["workflows"]["email_campaign"]
        workflow = self.get_workflow_by_name(workflow_config["name"])

        if not workflow:
            raise ValueError(f"Workflow '{workflow_config['name']}' not found")

        return self.execute_workflow(workflow["id"], campaign_data)

    def run_sms_campaign(self, campaign_data: Dict) -> Dict:
        """Run the SMS campaign workflow.

        Args:
            campaign_data: Campaign configuration and lead data

        Returns:
            Execution result
        """
        workflow_config = self.config["n8n"]["workflows"]["sms_campaign"]
        workflow = self.get_workflow_by_name(workflow_config["name"])

        if not workflow:
            raise ValueError(f"Workflow '{workflow_config['name']}' not found")

        return self.execute_workflow(workflow["id"], campaign_data)

    def setup_response_tracker(self) -> Dict:
        """Activate the response tracker workflow.

        Returns:
            Workflow activation status
        """
        workflow_config = self.config["n8n"]["workflows"]["response_tracker"]
        workflow = self.get_workflow_by_name(workflow_config["name"])

        if not workflow:
            raise ValueError(f"Workflow '{workflow_config['name']}' not found")

        # Activate workflow
        return self._make_request(
            "PATCH",
            f"workflows/{workflow['id']}",
            {"active": True}
        )

    def run_auto_followup(self) -> Dict:
        """Run the auto follow-up workflow.

        Returns:
            Execution result
        """
        workflow_config = self.config["n8n"]["workflows"]["auto_followup"]
        workflow = self.get_workflow_by_name(workflow_config["name"])

        if not workflow:
            raise ValueError(f"Workflow '{workflow_config['name']}' not found")

        return self.execute_workflow(workflow["id"])

    def get_workflow_statistics(self, workflow_id: str, days: int = 7) -> Dict:
        """Get execution statistics for a workflow.

        Args:
            workflow_id: Workflow ID
            days: Number of days to analyze

        Returns:
            Statistics summary
        """
        executions = self.get_executions(workflow_id, limit=100)

        stats = {
            "total_executions": len(executions),
            "successful": 0,
            "failed": 0,
            "running": 0,
            "average_duration": 0,
            "recent_executions": []
        }

        total_duration = 0
        completed_count = 0

        for execution in executions:
            status = execution.get("status")
            if status == "success":
                stats["successful"] += 1
            elif status == "error":
                stats["failed"] += 1
            elif status == "running":
                stats["running"] += 1

            # Calculate duration
            start_time = execution.get("startedAt")
            end_time = execution.get("stoppedAt")

            if start_time and end_time:
                start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                duration = (end - start).total_seconds()
                total_duration += duration
                completed_count += 1

            stats["recent_executions"].append({
                "id": execution.get("id"),
                "status": status,
                "started_at": start_time,
                "finished_at": end_time
            })

        if completed_count > 0:
            stats["average_duration"] = round(total_duration / completed_count, 2)

        return stats

    def health_check(self) -> Dict:
        """Check n8n instance health and connectivity.

        Returns:
            Health check results
        """
        try:
            workflows = self.list_workflows()
            return {
                "status": "healthy",
                "api_url": self.api_url,
                "total_workflows": len(workflows),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "api_url": self.api_url,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def main():
    """Command-line interface for n8n workflow manager."""
    import argparse

    parser = argparse.ArgumentParser(description="n8n Workflow Manager")
    parser.add_argument(
        "--list-workflows",
        action="store_true",
        help="List all workflows"
    )
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Check n8n instance health"
    )
    parser.add_argument(
        "--execute",
        type=str,
        help="Execute workflow by name"
    )
    parser.add_argument(
        "--stats",
        type=str,
        help="Get workflow statistics by ID"
    )

    args = parser.parse_args()

    manager = N8nWorkflowManager()

    if args.list_workflows:
        workflows = manager.list_workflows()
        print("\n📋 n8n Workflows:")
        for workflow in workflows:
            print(f"  - {workflow['name']} (ID: {workflow['id']})")
            print(f"    Active: {workflow.get('active', False)}")
            print()

    if args.health_check:
        health = manager.health_check()
        print("\n🏥 Health Check:")
        print(json.dumps(health, indent=2))

    if args.execute:
        workflow = manager.get_workflow_by_name(args.execute)
        if workflow:
            print(f"\n▶️  Executing workflow: {args.execute}")
            result = manager.execute_workflow(workflow["id"])
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Workflow '{args.execute}' not found")

    if args.stats:
        stats = manager.get_workflow_statistics(args.stats)
        print("\n📊 Workflow Statistics:")
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
