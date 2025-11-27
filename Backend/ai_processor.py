import json
import re

class AIProcessor:
    """AI-powered command processor for natural language understanding"""
    
    def __init__(self):
        self.command_patterns = {
            # Kubernetes Pods
            'get_pods': [
                r'(show|list|get|display|what|which).*pod',
                r'pod.*status',
                r'(what|which).*running',
                r'running.*pod',
                r'(show|get).*running'
            ],
            'describe_pod': [
                r'describe.*pod',
                r'detail.*pod',
                r'info.*pod'
            ],
            'delete_pod': [
                r'(delete|remove|kill).*pod',
                r'pod.*(delete|remove)'
            ],
            'restart_pod': [
                r'restart.*pod',
                r'pod.*restart'
            ],
            
            # Docker Containers
            'list_containers': [
                r'(show|list|get).*container',
                r'container.*running',
                r'what.*container'
            ],
            'list_images': [
                r'(show|list|get).*image',
                r'docker.*image'
            ],
            'stop_container': [
                r'stop.*container',
                r'container.*stop'
            ],
            
            # Kubernetes Services
            'get_services': [
                r'(show|list|get).*service',
                r'service.*status'
            ],
            
            # Kubernetes Deployments
            'get_deployments': [
                r'(show|list|get).*deployment',
                r'deployment.*status'
            ],
            'scale_deployment': [
                r'scale.*deployment',
                r'deployment.*scale',
                r'increase.*replica',
                r'decrease.*replica'
            ],
            
            # Logs
            'get_logs': [
                r'(show|get|display).*log',
                r'log.*pod',
                r'log.*container'
            ],
            
            # Health & Status
            'health_check': [
                r'health.*check',
                r'system.*status',
                r'check.*health',
                r'status.*system'
            ],
            
            # Nodes
            'get_nodes': [
                r'(show|list|get).*node',
                r'node.*status'
            ]
        }
    
    def process_command(self, voice_command):
        """Process voice command and return structured action"""
        command_lower = voice_command.lower()
        
        # Detect command type
        command_type = self.detect_command_type(command_lower)
        
        # Extract parameters
        params = self.extract_parameters(command_lower)
        
        # Generate response
        result = {
            'original_command': voice_command,
            'command_type': command_type,
            'parameters': params,
            'action': self.get_action(command_type, params),
            'description': self.get_description(command_type, params)
        }
        
        return result
    
    def detect_command_type(self, command):
        """Detect what type of command user wants"""
        for cmd_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    return cmd_type
        return 'unknown'
    
    def extract_parameters(self, command):
        """Extract parameters like pod name, replica count, etc."""
        params = {}
        
        # Extract pod/container name
        name_match = re.search(r'(pod|container|deployment|service)\s+(\w+)', command)
        if name_match:
            params['name'] = name_match.group(2)
        
        # Extract replica count
        replica_match = re.search(r'(\d+)\s*(replica|instance|pod)', command)
        if replica_match:
            params['replicas'] = int(replica_match.group(1))
        
        # Extract namespace
        namespace_match = re.search(r'namespace\s+(\w+)', command)
        if namespace_match:
            params['namespace'] = namespace_match.group(1)
        
        return params
    
    def get_action(self, command_type, params):
        """Get the actual command to execute"""
        actions = {
            'get_pods': 'kubectl get pods',
            'describe_pod': f"kubectl describe pod {params.get('name', '')}",
            'delete_pod': f"kubectl delete pod {params.get('name', '')}",
            'restart_pod': f"kubectl rollout restart deployment {params.get('name', '')}",
            'list_containers': 'docker ps -a',
            'list_images': 'docker images',
            'stop_container': f"docker stop {params.get('name', '')}",
            'get_services': 'kubectl get services',
            'get_deployments': 'kubectl get deployments',
            'scale_deployment': f"kubectl scale deployment {params.get('name', '')} --replicas={params.get('replicas', 3)}",
            'get_logs': f"kubectl logs {params.get('name', '')}",
            'health_check': 'system_health',
            'get_nodes': 'kubectl get nodes',
            'unknown': 'unknown'
        }
        return actions.get(command_type, 'unknown')
    
    def get_description(self, command_type, params):
        """Get human-readable description"""
        descriptions = {
            'get_pods': 'Fetching all pods in the cluster',
            'describe_pod': f"Getting detailed information about pod: {params.get('name', 'unknown')}",
            'delete_pod': f"Deleting pod: {params.get('name', 'unknown')}",
            'restart_pod': f"Restarting deployment: {params.get('name', 'unknown')}",
            'list_containers': 'Listing all Docker containers',
            'list_images': 'Showing all Docker images',
            'stop_container': f"Stopping container: {params.get('name', 'unknown')}",
            'get_services': 'Fetching all Kubernetes services',
            'get_deployments': 'Listing all deployments',
            'scale_deployment': f"Scaling deployment {params.get('name', '')} to {params.get('replicas', 3)} replicas",
            'get_logs': f"Fetching logs for: {params.get('name', 'unknown')}",
            'health_check': 'Checking system health status',
            'get_nodes': 'Listing all cluster nodes',
            'unknown': 'Command not recognized'
        }
        return descriptions.get(command_type, 'Processing command...')
    
    def generate_smart_response(self, command_result, ai_analysis):
        """Generate intelligent response based on command output"""
        output = command_result.lower()
        
        # Analyze output
        if 'running' in output:
            running_count = output.count('running')
            response = f"✅ Found {running_count} running pod(s). "
        elif 'error' in output or 'failed' in output:
            response = "⚠️ There seems to be an issue. "
        elif 'no resources found' in output:
            response = "ℹ️ No resources found. "
        else:
            response = "✅ Command executed successfully. "
        
        return response + f"\n\n{command_result}"
