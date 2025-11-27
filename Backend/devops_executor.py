import subprocess
import json

class DevOpsExecutor:
    def execute_command(self, voice_command):
        """Execute DevOps commands based on voice input"""
        command_lower = voice_command.lower()
        
        # Fix common voice recognition errors
        command_lower = command_lower.replace('boats', 'pods')
        command_lower = command_lower.replace('ports', 'pods')
        command_lower = command_lower.replace('pots', 'pods')
        command_lower = command_lower.replace('what', 'show')
        command_lower = command_lower.replace('which', 'show')
        
        try:
            # Kubernetes Commands  
            if 'pod' in command_lower or 'pods' in command_lower or 'running' in command_lower:
                if 'show' in command_lower or 'list' in command_lower or 'get' in command_lower:
                    return self.run_kubectl('get pods')
                elif 'describe' in command_lower:
                    return self.run_kubectl('describe pods')
            
            # Docker Commands
            elif 'container' in command_lower or 'containers' in command_lower:
                if 'list' in command_lower or 'show' in command_lower:
                    return self.run_docker('ps -a')
                elif 'running' in command_lower:
                    return self.run_docker('ps')
            
            elif 'image' in command_lower or 'images' in command_lower:
                return self.run_docker('images')
            
            # System Commands
            elif 'health' in command_lower or 'status' in command_lower:
                return self.check_system_health()
            
            # Kubernetes Services
            elif 'service' in command_lower or 'services' in command_lower:
                return self.run_kubectl('get services')
            
            # Kubernetes Deployments
            elif 'deployment' in command_lower or 'deployments' in command_lower:
                return self.run_kubectl('get deployments')
            
            # Kubernetes Nodes
            elif 'node' in command_lower or 'nodes' in command_lower:
                return self.run_kubectl('get nodes')
            
            # Logs
            elif 'log' in command_lower:
                # Extract container/pod name
                words = voice_command.lower().replace('-', ' ').split()
                container_name = None
                
                # Look for common names
                for word in words:
                    if word in ['backend', 'frontend', 'database', 'redis', 'nginx', 'mysql']:
                        container_name = word
                        break
                
                if container_name:
                    # Try Docker first
                    docker_result = self.get_docker_logs(container_name)
                    if 'Error' not in docker_result:
                        return docker_result
                    # Fallback to kubectl
                    return self.run_kubectl(f'logs {container_name} --tail=50')
                else:
                    return "Please specify container/pod name. Example: 'show logs of backend'"
            
            # Namespaces
            elif 'namespace' in command_lower:
                return self.run_kubectl('get namespaces')
            
            # ConfigMaps
            elif 'configmap' in command_lower:
                return self.run_kubectl('get configmaps')
            
            # Secrets
            elif 'secret' in command_lower:
                return self.run_kubectl('get secrets')
            
            else:
                return f"Command '{voice_command}' recognized but not implemented yet. Try: show pods, list containers, get services, show logs"
                
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    def run_kubectl(self, command):
        """Execute kubectl commands"""
        try:
            full_command = f"kubectl {command}"
            result = subprocess.run(
                full_command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    return f"✅ Kubectl Output:\n{output}"
                else:
                    return "✅ Command executed successfully (no output)"
            else:
                error = result.stderr.strip()
                if 'not found' in error.lower() or 'is not recognized' in error.lower():
                    return "❌ kubectl not installed. Install kubectl or use Docker commands instead."
                return f"❌ Kubectl Error:\n{error}"
                
        except subprocess.TimeoutExpired:
            return "⏱️ Command timeout. Please try again."
        except Exception as e:
            return f"❌ Error running kubectl: {str(e)}"
    
    def run_docker(self, command):
        """Execute docker commands"""
        try:
            full_command = f"docker {command}"
            result = subprocess.run(
                full_command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    return f"✅ Docker Output:\n{output}"
                else:
                    return "✅ No containers found or command executed successfully"
            else:
                error = result.stderr.strip()
                if 'not found' in error.lower() or 'is not recognized' in error.lower():
                    return "❌ Docker not installed or not running. Please start Docker Desktop."
                return f"❌ Docker Error:\n{error}"
                
        except subprocess.TimeoutExpired:
            return "⏱️ Command timeout. Please try again."
        except Exception as e:
            return f"❌ Error running docker: {str(e)}"
    
    def get_docker_logs(self, container_name):
        """Get logs from Docker container"""
        try:
            # First, find container with matching name
            ps_result = subprocess.run(
                f'docker ps --filter "name={container_name}" --format "{{{{.Names}}}}"',
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if ps_result.returncode == 0 and ps_result.stdout.strip():
                actual_name = ps_result.stdout.strip().split('\n')[0]
                
                # Get logs
                logs_result = subprocess.run(
                    f'docker logs {actual_name} --tail 30',
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if logs_result.returncode == 0:
                    logs = logs_result.stdout.strip()
                    if logs:
                        return f"✅ Docker Logs for {actual_name}:\n{logs}"
                    else:
                        return f"✅ Container {actual_name} has no logs yet"
            
            return f"❌ No running container found with name: {container_name}"
            
        except Exception as e:
            return f"❌ Error getting Docker logs: {str(e)}"
    
    def check_system_health(self):
        """Check system health"""
        health_info = []
        
        # Check Docker
        try:
            docker_result = subprocess.run(
                "docker info", 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=5
            )
            if docker_result.returncode == 0:
                health_info.append("✅ Docker: Running")
            else:
                health_info.append("❌ Docker: Not running")
        except:
            health_info.append("❌ Docker: Not available")
        
        # Check Kubectl
        try:
            kubectl_result = subprocess.run(
                "kubectl version --client", 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=5
            )
            if kubectl_result.returncode == 0:
                health_info.append("✅ Kubectl: Installed")
            else:
                health_info.append("❌ Kubectl: Not installed")
        except:
            health_info.append("❌ Kubectl: Not available")
        
        return "System Health Check:\n" + "\n".join(health_info)
