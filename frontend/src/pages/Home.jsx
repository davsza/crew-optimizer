import { useState, useEffect } from "react";
import api from "../api";
import ShiftSchedule from "../components/ShiftSchedule";
import Header from "../components/Header";
import "../styles/Home.css";
import axios from "axios";

function getCurrentWeek() {
  const now = new Date();
  const yearStart = new Date(now.getFullYear(), 0, 0);
  const diff = now - yearStart;
  const oneWeek = 1000 * 60 * 60 * 24 * 7;
  const weekNumber = Math.floor(diff / oneWeek) + 1;
  return "W" + weekNumber;
}

function getDefaultShift() {
  return "000000000000000000000";
}

function Home() {
  const [shift, setShifts] = useState([]);
  const [appliedShift, setAppliedShift] = useState("");
  const [userGroup, setUserGroup] = useState("");

  const getShift = () => {
    api
      .get("/api/shifts/")
      .then((res) => res.data)
      .then((data) => {
        setShifts(data[0]);
      })
      .catch((err) => alert(err));
  };

  const fetchUserGroup = async () => {
    console.log("Fetch")
    try {
      console.log("Try")
      const response = await axios.get("/api/get-user-group");
      setUserGroup(response.data.group);
      console.log("response", response.data.group);
    } catch (error) {
      console.log("Error")
    }
  };

  useEffect(() => {
    getShift();
    fetchUserGroup();
  }, []);

  const createShift = (e) => {
    e.preventDefault();

    const week = getCurrentWeek();
    const actualShift = getDefaultShift();
    const currDateTime = new Date();
    const isoDateTime = currDateTime.toISOString();

    api
      .post("/api/shifts/", {
        week: week,
        applied_shift: appliedShift,
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
        getShift();
      })
      .catch((err) => alert(err));
  };

  return (
    <div>
      <Header></Header>
      <div className="container">
        <div className="schedule-container">
          <h2>Shifts</h2>
          {shift === undefined ? (
            <ShiftSchedule schedule={getDefaultShift()} />
          ) : (
            <ShiftSchedule schedule={shift.applied_shift} />
          )}
        </div>
        <div className="chat-container">
          <h2>Create a shift</h2>
          <form onSubmit={createShift}>
            <label htmlFor="content">Applied schedule:</label>
            <br />
            <textarea
              id="content"
              name="content"
              required
              value={appliedShift}
              onChange={(e) => setAppliedShift(e.target.value)}
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
