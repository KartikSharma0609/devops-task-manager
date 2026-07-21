def test_get_tasks(client):

    response = client.get("/tasks")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)

    if len(data) > 0:

        task = data[0]

        assert "id" in task
        assert "title" in task
        assert "status" in task
