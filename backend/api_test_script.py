#!/usr/bin/env python
# api_test_script.py
"""
Simple script to test the Derby Director API endpoints
This script will make real requests to a running Derby Director API server
"""

import sys
import asyncio
import json
from typing import Dict, Any, Optional

import httpx


class DerbyDirectorTester:
    """Class to test the Derby Director API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def login(self, username: str = "admin", password: str = "derby2023") -> bool:
        """Login to the API and get a token"""
        try:
            response = await self.client.post(
                "/auth/login", 
                json={"username": username, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.headers["Authorization"] = f"Bearer {self.token}"
                print(f"✅ Successfully logged in as {username}")
                return True
            else:
                print(f"❌ Login failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error during login: {str(e)}")
            return False
    
    async def test_divisions(self):
        """Test division endpoints"""
        print("\n=== Testing Division Endpoints ===")
        
        # Get all divisions
        try:
            response = await self.client.get("/divisions/", headers=self.headers)
            if response.status_code == 200:
                divisions = response.json()
                print(f"✅ Retrieved {len(divisions)} divisions")
                
                # Show divisions
                for dvsn in divisions:
                    print(f"  - Division ID {dvsn['id']}: {dvsn['name']}")
                
                # Return first division ID for future tests
                return divisions[0]["id"] if divisions else None
            else:
                print(f"❌ Failed to get divisions: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting divisions: {str(e)}")
            return None
    
    async def test_racers(self, division_id: Optional[int] = None):
        """Test racer endpoints"""
        print("\n=== Testing Racer Endpoints ===")
        
        if not division_id:
            print("⚠️ No division ID provided, trying to get one...")
            division_id = await self.test_divisions()
            if not division_id:
                print("❌ Cannot test racers without a valid division ID")
                return None
        
        # Get all racers
        try:
            response = await self.client.get("/racers/", headers=self.headers)
            if response.status_code == 200:
                racers = response.json()
                print(f"✅ Retrieved {len(racers)} racers")
                
                # Show first few racers
                for racer in racers[:5]:
                    print(f"  - Racer ID {racer['id']}: {racer['firstname']} {racer['lastname']} (Car #{racer['carno']})")
                
                if len(racers) > 5:
                    print(f"  ... and {len(racers) - 5} more")
                
                # Test creating a racer
                new_racer = {
                    "firstname": "Test",
                    "lastname": "Racer",
                    "divisionid": division_id,
                    "carno": "T123",
                    "carname": "Script Speedster"
                }
                
                create_response = await self.client.post(
                    "/racers/", 
                    json=new_racer,
                    headers=self.headers
                )
                
                if create_response.status_code == 201:
                    created_racer = create_response.json()
                    print(f"✅ Created new racer: {created_racer['firstname']} {created_racer['lastname']}")
                    racer_id = created_racer["id"]
                    
                    # Test updating the racer
                    update_response = await self.client.put(
                        f"/racers/{racer_id}",
                        json={"carname": "Updated Speedster"},
                        headers=self.headers
                    )
                    
                    if update_response.status_code == 200:
                        updated_racer = update_response.json()
                        print(f"✅ Updated racer car name to: {updated_racer['carname']}")
                    else:
                        print(f"❌ Failed to update racer: {update_response.status_code}")
                    
                    return racer_id
                else:
                    print(f"❌ Failed to create racer: {create_response.status_code}")
                    return racers[0]["id"] if racers else None
            else:
                print(f"❌ Failed to get racers: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error testing racers: {str(e)}")
            return None
    
    async def test_heats(self):
        """Test heat endpoints"""
        print("\n=== Testing Heat Endpoints ===")
        
        # Get all heats
        try:
            response = await self.client.get("/heats/", headers=self.headers)
            if response.status_code == 200:
                heats = response.json()
                print(f"✅ Retrieved {len(heats)} heats")
                
                if heats:
                    # Get details for the first heat
                    heat_id = heats[0]["id"]
                    detail_response = await self.client.get(
                        f"/heats/{heat_id}",
                        headers=self.headers
                    )
                    
                    if detail_response.status_code == 200:
                        heat_detail = detail_response.json()
                        print(f"✅ Heat #{heat_detail['heat']} details:")
                        print(f"  - Round: {heat_detail['round_name']}")
                        print(f"  - Status: {heat_detail['status']}")
                        print(f"  - Lanes: {len(heat_detail['lanes'])}")
                        
                        return heat_id
                    else:
                        print(f"❌ Failed to get heat details: {detail_response.status_code}")
                        return heat_id
                else:
                    print("⚠️ No heats found")
                    return None
            else:
                print(f"❌ Failed to get heats: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error testing heats: {str(e)}")
            return None
    
    async def test_results(self, heat_id: Optional[int] = None):
        """Test result endpoints"""
        print("\n=== Testing Result Endpoints ===")
        
        if not heat_id:
            print("⚠️ No heat ID provided, trying to get one...")
            heat_id = await self.test_heats()
            if not heat_id:
                print("❌ Cannot test results without a valid heat ID")
                return
        
        # Get heat details
        try:
            detail_response = await self.client.get(
                f"/heats/{heat_id}",
                headers=self.headers
            )
            
            if detail_response.status_code == 200:
                heat_detail = detail_response.json()
                lanes = heat_detail["lanes"]
                
                if not lanes:
                    print("❌ Heat has no lane assignments")
                    return
                
                # Create fake results
                results = []
                for i, lane in enumerate(lanes):
                    results.append({
                        "heat_id": heat_id,
                        "racer_id": lane["racer_id"],
                        "lane": lane["lane"],
                        "time": 3.0 + (i * 0.1),  # Fake times
                        "place": i + 1
                    })
                
                # Submit results for this heat
                heat_results = {
                    "heat_id": heat_id,
                    "results": results
                }
                
                record_response = await self.client.post(
                    "/results/heat",
                    json=heat_results,
                    headers=self.headers
                )
                
                if record_response.status_code == 201:
                    print(f"✅ Recorded results for heat #{heat_detail['heat']}")
                    
                    # Get the results back
                    get_results_response = await self.client.get(
                        f"/results/heat/{heat_id}",
                        headers=self.headers
                    )
                    
                    if get_results_response.status_code == 200:
                        result_data = get_results_response.json()
                        print(f"✅ Retrieved results for heat:")
                        
                        for result in result_data["results"]:
                            print(f"  - Lane {result['lane']}: {result['racer_name']} - {result['time']}s ({result['place']} place)")
                    else:
                        print(f"❌ Failed to get results: {get_results_response.status_code}")
                else:
                    print(f"❌ Failed to record results: {record_response.status_code}")
            else:
                print(f"❌ Failed to get heat details: {detail_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing results: {str(e)}")


async def main():
    """Main entry point"""
    # Check if a different base URL was provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"Testing Derby Director API at {base_url}")
    print("Make sure the API server is running!\n")
    
    tester = DerbyDirectorTester(base_url)
    
    try:
        # Login first
        if not await tester.login():
            print("Cannot proceed with tests without successful login")
            return
        
        # Run the tests
        division_id = await tester.test_divisions()
        racer_id = await tester.test_racers(division_id)
        heat_id = await tester.test_heats()
        await tester.test_results(heat_id)
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Error during tests: {str(e)}")
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())