def test_home(client):

    print("\n--- ROUTES IN CI ---")
    print(client.application.url_map)
    print("--------------------\n")

    response = client.get("/system", follow_redirects=True)

    assert response.status_code == 200

    assert response.get_json() == {"message": "DevOps Task Manager API is running"}
