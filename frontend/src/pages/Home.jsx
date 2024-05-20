import { useState, useEffect } from "react";
import api from "../api";
import ShiftPanel from "../components/ShitPanel";
import Header from "../components/Header";
import Dropdown from "../components/Dropdown";
import "../styles/Home.css";
import { getCurrentWeek, getCurrentYear } from "../constants";

function Home() {
  const week = getCurrentWeek(0);
  const appliedShiftWeek = getCurrentWeek(2);

  const year = getCurrentYear();

  const [finalShift, setFinalShift] = useState([]);
  const [appliedShift, setAppliedShift] = useState([]);
  const [selectedWeekForFinalShifts, setSelectedWeekForFinalShifts] =
    useState(week);
  const [selectedWeekForAppliedShifts, setSelectedWeekForAppliedShifts] =
    useState(appliedShiftWeek);
  const [application, setApplication] = useState("");
  const [userGroup, setUserGroup] = useState("");
  const [userName, setUserName] = useState("");

  const getFinalShift = (week) => {
    api
      .get(`/api/shifts/${week}`)
      .then((res) => res.data)
      .then((data) => {
        setFinalShift(data[0]);
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
    getFinalShift(week);
    getAppliedShift(appliedShiftWeek);
    fetchUserDate();
  }, []);

  useEffect(() => {
    getFinalShift(selectedWeekForFinalShifts);
  }, [selectedWeekForFinalShifts]);

  useEffect(() => {
    getAppliedShift(selectedWeekForAppliedShifts);
  }, [selectedWeekForAppliedShifts]);

  const handleSelectWeekForFinalShifts = (week) => {
    setSelectedWeekForFinalShifts(week);
  };

  const handleSelectWeekForAppliedShifts = (week) => {
    setSelectedWeekForAppliedShifts(week);
  };

  const createAppliedShift = (e) => {
    e.preventDefault();

    const week = getCurrentWeek(2);
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
        getAppliedShift(appliedShiftWeek);
      })
      .catch((err) => alert(err));
  };

  return (
    <div>
      <Header userName={userName}></Header>
      <div className="container">
        <div className="schedule-container">
          {userGroup !== "Supervisor" ? (
            <>
              <Dropdown
                year={year}
                finalShifts={true}
                onSelectWeek={handleSelectWeekForFinalShifts}
              />
              <Dropdown
                year={year}
                finalShifts={false}
                onSelectWeek={handleSelectWeekForAppliedShifts}
              />
              {finalShift === undefined ? (
                <p>No shift</p>
              ) : (
                <ShiftPanel
                  actualShift={finalShift}
                  appliedShift={appliedShift}
                />
              )}
            </>
          ) : (
            <p>Supervisior</p>
          )}
        </div>
        <div className="chat-container">
          <form className="chat-form" onSubmit={createAppliedShift}>
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
