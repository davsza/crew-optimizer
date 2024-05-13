import { useState, useEffect } from "react";
import api from "../api";
import ShiftPanel from "../components/ShitPanel";
import Header from "../components/Header";
import Dropdown from "../components/Dropdown";
import "../styles/Home.css";
import { getCurrentWeek, getCurrentYear } from "../constants";

function Home() {
  const [actualShift, setActualShifts] = useState([]);
  const [appliedShift, setAppliedShift] = useState([]);
  const [selectedWeek, setSelectedWeek] = useState(getCurrentWeek(0));
  const [application, setApplication] = useState("");
  const [userGroup, setUserGroup] = useState("");
  const [userName, setUserName] = useState("");

  const getActualShift = (week) => {
    api
      .get(`/api/shifts/${week}`)
      .then((res) => res.data)
      .then((data) => {
        setActualShifts(data[0]);
      })
      .catch((err) => alert(err));
  };

  const getAppliedShift = (week) => {
    api
      .get(`/api/shifts/${week}`)
      .then((res) => res.data)
      .then((data) => {
        setAppliedShift(data[0]);
      })
      .catch((err) => alert(err));
  };

  const fetchUserDate = () => {
    api
      .get("/api/get-user-data/")
      .then((res) => res.data)
      .then((data) => {
        setUserGroup(data.group);
        setUserName(data.username);
      })
      .catch((err) => alert(err));
  };

  useEffect(() => {
    const week = getCurrentWeek(0);
    const appliedShiftWeek = week + 2;
    getActualShift(week);
    getAppliedShift(appliedShiftWeek);
    fetchUserDate();
  }, []);

  useEffect(() => {
    getActualShift(selectedWeek);
  }, [selectedWeek]);

  const handleSelectWeek = (week) => {
    setSelectedWeek(week);
  };

  const createShift = (e) => {
    e.preventDefault();

    const week = getCurrentWeek(0);
    const actualShift = "0".repeat(21);
    const currDateTime = new Date();
    const isoDateTime = currDateTime.toISOString();
    const year = currDateTime.getFullYear();

    api
      .post("/api/shifts/", {
        week: week,
        year: year,
        applied_shift: application,
        actual_shift: actualShift,
        application_last_modified: isoDateTime,
        actual_last_modified: isoDateTime,
      })
      .then((res) => {
        if (res.status === 201) {
          console.log("Shift created");
        } else {
          console.log("Failed to make a shift");
        }
        getActualShift();
      })
      .catch((err) => alert(err));
  };

  return (
    <div>
      <Header userName={userName}></Header>
      <div className="container">
        <div className="schedule-container">
          {userGroup !== "Supervisior" ? (
            <>
              <h2>Shifts</h2>
              <Dropdown
                year={getCurrentYear()}
                onSelectWeek={handleSelectWeek}
              />
              {actualShift === undefined ? (
                <p>No shift</p>
              ) : (
                <ShiftPanel
                  actualShift={actualShift}
                  appliedShift={appliedShift}
                />
              )}
            </>
          ) : (
            <p>Supervisior</p>
          )}
        </div>
        <div className="chat-container">
          <h2>Create a shift</h2>
          <form className="chat-form" onSubmit={createShift}>
            <label htmlFor="content">Application:</label>
            <br />
            <textarea
              id="content"
              name="content"
              required
              value={application}
              onChange={(e) => setApplication(e.target.value)}
            ></textarea>
            <br />
            <input type="submit" value="Submit"></input>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Home;
