# derby_director/tests/test_api.py
"""
Tests for the Derby Director API
"""

import asyncio
import pytest
from httpx import AsyncClient
from litestar.testing import TestClient

from backend.main import app


@pytest.mark.asyncio
async def test_login():
    """Test authentication endpoints"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Log in with the admin credentials from seed data
        login_data = {
            "username": "admin",
            "password": "derby2023"
        }
        response = await client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Use the token to access protected endpoint
        token = data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get current user
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["username"] == "admin"
        assert user_data["is_admin"] is True


@pytest.mark.asyncio
async def test_divisions():
    """Test division endpoints"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Log in first
        login_data = {"username": "admin", "password": "derby2023"}
        response = await client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get all divisions
        response = await client.get("/divisions/", headers=headers)
        assert response.status_code == 200
        divisions = response.json()
        assert len(divisions) > 0
        
        # Create a new division
        new_division = {
            "name": "Test Division",
            "sort_order": 10
        }
        response = await client.post("/divisions/", json=new_division, headers=headers)
        assert response.status_code == 201
        created_division = response.json()
        assert created_division["name"] == "Test Division"
        
        # Get a specific division
        division_id = created_division["id"]
        response = await client.get(f"/divisions/{division_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == "Test Division"
        
        # Update the division
        update_data = {
            "name": "Updated Division",
            "sort_order": 11
        }
        response = await client.put(f"/divisions/{division_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        updated_division = response.json()
        assert updated_division["name"] == "Updated Division"
        
        # Delete the division
        response = await client.delete(f"/divisions/{division_id}", headers=headers)
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_racers():
    """Test racer endpoints"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Log in first
        login_data = {"username": "admin", "password": "derby2023"}
        response = await client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get all racers
        response = await client.get("/racers/", headers=headers)
        assert response.status_code == 200
        racers = response.json()
        assert len(racers) > 0
        
        # Get divisions to use for creating a racer
        response = await client.get("/divisions/", headers=headers)
        divisions = response.json()
        division_id = divisions[0]["id"]
        
        # Create a new racer
        new_racer = {
            "firstname": "Test",
            "lastname": "Racer",
            "divisionid": division_id,
            "carno": "T1",
            "carname": "Test Speeder"
        }
        response = await client.post("/racers/", json=new_racer, headers=headers)
        assert response.status_code == 201
        created_racer = response.json()
        assert created_racer["firstname"] == "Test"
        assert created_racer["lastname"] == "Racer"
        
        # Get a specific racer
        racer_id = created_racer["id"]
        response = await client.get(f"/racers/{racer_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["firstname"] == "Test"
        
        # Update the racer
        update_data = {
            "firstname": "Updated",
            "carname": "Speed Demon"
        }
        response = await client.put(f"/racers/{racer_id}", json=update_data, headers=headers)
        assert response.status_code == 200
        updated_racer = response.json()
        assert updated_racer["firstname"] == "Updated"
        assert updated_racer["carname"] == "Speed Demon"
        
        # Delete the racer
        response = await client.delete(f"/racers/{racer_id}", headers=headers)
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_heats():
    """Test heat endpoints"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Log in first
        login_data = {"username": "admin", "password": "derby2023"}
        response = await client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get all heats
        response = await client.get("/heats/", headers=headers)
        assert response.status_code == 200
        heats = response.json()
        assert len(heats) > 0
        
        # Get upcoming heats
        response = await client.get("/heats/?upcoming=true", headers=headers)
        assert response.status_code == 200
        
        # Get a specific heat
        heat_id = heats[0]["id"]
        response = await client.get(f"/heats/{heat_id}", headers=headers)
        assert response.status_code == 200
        heat_detail = response.json()
        assert "lanes" in heat_detail
        assert "round_name" in heat_detail


@pytest.mark.asyncio
async def test_results():
    """Test result endpoints"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Log in first
        login_data = {"username": "admin", "password": "derby2023"}
        response = await client.post("/auth/login", json=login_data)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get all results (might be empty if no races completed)
        response = await client.get("/results/", headers=headers)
        assert response.status_code == 200
        
        # Get heats to use for recording results
        response = await client.get("/heats/", headers=headers)
        heats = response.json()
        
        if heats:
            # Get a specific heat
            heat_id = heats[0]["id"]
            response = await client.get(f"/heats/{heat_id}", headers=headers)
            heat_detail = response.json()
            
            if heat_detail["lanes"]:
                # Record results for this heat
                results = []
                for i, lane in enumerate(heat_detail["lanes"]):
                    results.append({
                        "heat_id": heat_id,
                        "racer_id": lane["racer_id"],
                        "lane": lane["lane"],
                        "time": 3.0 + (i * 0.1),  # Fake times
                        "place": i + 1
                    })
                
                heat_results = {
                    "heat_id": heat_id,
                    "results": results
                }
                
                response = await client.post("/results/heat", json=heat_results, headers=headers)
                assert response.status_code == 201
                
                # Get results for this heat
                response = await client.get(f"/results/heat/{heat_id}", headers=headers)
                assert response.status_code == 200
                result_data = response.json()
                assert result_data["heat_id"] == heat_id
                assert len(result_data["results"]) > 0
                
                # Delete results for this heat
                response = await client.delete(f"/results/heat/{heat_id}", headers=headers)
                assert response.status_code == 204