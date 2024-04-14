import { useState, useEffect } from "react";
import api from "../api";
import ShiftSchedule from "../components/Shift";
import "../styles/Home.css";

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

  let schedule = getDefaultShift();

  useEffect(() => {
    getShift();
  }, []);

  const getShift = () => {
    api
      .get("/api/shifts/")
      .then((res) => res.data)
      .then((data) => {
        setShifts(data);
        console.log(shift);
      })
      .catch((err) => alert(err));
    shift.map((s) => {
      schedule = s.applied_shift;
    });
  };

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
          alert("Shift created");
        } else {
          alert("Failed to make a shift");
        }
        getShift();
      })
      .catch((err) => alert(err));
  };

  return (
    <div>
      <div>
        <h2>Shifts</h2>
        <ShiftSchedule schedule={schedule} />
      </div>
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
  );
}

export default Home;
