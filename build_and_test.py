#!/usr/bin/env python3
# build_and_test.py - Complete project setup and testing for AI Retouch Studio

import os
import sys
import subprocess
import time
from pathlib import Path

import requests


class AIRetouchBuilder:
    def __init__(self):
        self.root_dir = Path(__file__).parent.resolve()
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"
        self.infra_dir = self.root_dir / "infrastructure"

    def run_command(self, cmd, cwd=None, check=True):
        cwd = cwd or self.root_dir
        print(f"\n🚀 Running: {cmd}")
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if check and result.returncode != 0:
            print(f"❌ Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            sys.exit(1)
        return result

    def check_prerequisites(self):
        print("🔍 Checking prerequisites...")
        # Docker
        docker = self.run_command("docker --version", check=False)
        if docker.returncode != 0:
            print("❌ Docker not found. Please install Docker Desktop.")
            sys.exit(1)
        # Docker Compose (docker compose or docker-compose)
        compose = self.run_command("docker compose version", check=False)
        if compose.returncode != 0:
            compose_alt = self.run_command("docker-compose --version", check=False)
            if compose_alt.returncode != 0:
                print("❌ Docker Compose not found. Install Docker Compose v2 or v1.")
                sys.exit(1)
        print("✅ All prerequisites met")

    def setup_development(self):
        print("⚙️  Setting up development environment...")
        # Backend deps
        req = self.backend_dir / "requirements.txt"
        if req.exists():
            print("📦 Installing Python dependencies...")
            self.run_command(f"pip install -r \"{req}\"")
        # Frontend deps (optional)
        pkg = self.frontend_dir / "package.json"
        if pkg.exists():
            print("📦 Installing frontend dependencies...")
            self.run_command("npm install", cwd=self.frontend_dir, check=False)

    def build_infrastructure(self):
        print("🐳 Building infrastructure...")
        # Prefer bash script if available, else fallback to compose
        start_script = self.infra_dir / "start-dev.sh"
        if start_script.exists():
            # Make executable on Unix, ignore error on Windows
            try:
                os.chmod(start_script, 0o755)
            except Exception:
                pass
            self.run_command(f"\"{start_script}\"", cwd=self.infra_dir)
        else:
            self.run_command("docker compose up --build", cwd=self.infra_dir)

        print("⏳ Waiting for services to start...")
        time.sleep(5)
        # Health probe
        for i in range(30):
            try:
                response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Backend service is healthy")
                    return
            except Exception:
                pass
            print(f"⏳ Waiting for backend... ({i+1}/30)")
            time.sleep(5)
        print("❌ Backend failed to start in time")
        sys.exit(1)

    def download_models(self):
        print("🤖 Checking AI models...")
        models_dir = self.root_dir / "models"
        models_dir.mkdir(exist_ok=True)
        download_script = self.backend_dir / "scripts" / "download_models.py"
        if download_script.exists():
            print("📥 Downloading AI models...")
            self.run_command(f"python \"{download_script}\"", cwd=self.backend_dir)
        else:
            print("⚠️  Model download script not found. Models will download on first use.")

    def run_tests(self):
        print("🧪 Running test suite...")
        tests_dir = self.root_dir / "quality" / "tests"
        if tests_dir.exists():
            self.run_command(f"python -m pytest \"{tests_dir}\" -q", check=False)
        else:
            print("⚠️  No tests found, skipping.")

    def check_ai_capabilities(self):
        print("🔬 Checking AI capabilities...")
        try:
            response = requests.get("http://localhost:8000/api/v1/retouch/capabilities", timeout=10)
            if response.status_code == 200:
                capabilities = response.json()
                print("✅ AI Capabilities:")
                print(f"   - Models loaded: {capabilities.get('models_loaded', False)}")
                caps = capabilities.get('capabilities', [])
                print(f"   - Available features: {', '.join(caps)}")
            else:
                print("❌ Failed to get AI capabilities")
        except Exception as e:
            print(f"❌ AI capability check failed: {e}")

    def show_status(self):
        print("\n" + "=" * 50)
        print("🎉 AI RETOUCH STUDIO - STATUS REPORT")
        print("=" * 50)
        services = {
            "Backend API": "http://localhost:8000/api/v1/health",
            "API Documentation": "http://localhost:8000/docs",
            "Redis": "redis://localhost:6379",
            "PostgreSQL": "postgresql://localhost:5432",
        }
        for service, url in services.items():
            try:
                if url.startswith("http"):
                    r = requests.get(url, timeout=2)
                    status = "✅ RUNNING" if r.status_code == 200 else "❌ DOWN"
                else:
                    status = "✅ CONFIGURED"
            except Exception:
                status = "❌ DOWN"
            print(f"{service:20} {status}")
        print("\n🚀 NEXT STEPS:")
        print("1. Load Photoshop panel from frontend/ directory")
        print("2. Test AI retouching at http://localhost:8000/docs")
        print("3. Implement Photoshop API bridge in frontend/src/photoshop-bridge.js")
        print("4. Add SAM model integration for precise masking")

    def run(self):
        print("🚀 AI RETOUCH STUDIO - BUILD & TEST SCRIPT")
        print("=" * 50)
        try:
            self.check_prerequisites()
            self.setup_development()
            self.build_infrastructure()
            self.download_models()
            self.run_tests()
            self.check_ai_capabilities()
            self.show_status()
        except Exception as e:
            print(f"❌ Build failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    AIRetouchBuilder().run()
