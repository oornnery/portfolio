from app.models.profile import Profile


def test_profile_model_json_fields():
    profile = Profile(user_id=1)

    work_data = [
        {
            "title": "Developer",
            "company": "Tech Corp",
            "start_date": "2020",
            "end_date": "Present",
            "description": "Coding",
        }
    ]

    profile.work_experience = work_data

    assert profile.work_experience[0]["title"] == "Developer"
    assert profile.work_experience[0]["company"] == "Tech Corp"


def test_profile_skills():
    profile = Profile(user_id=1)
    skills = ["Python", "FastAPI"]
    profile.skills = skills

    assert "Python" in profile.skills
    assert len(profile.skills) == 2
