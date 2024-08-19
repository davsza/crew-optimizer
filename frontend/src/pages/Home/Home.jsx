import { useState, useEffect } from "react";
import api from "../../api";
import ShiftPanel from "../../components/ShiftPanel/ShitPanel";
import Header from "../../components/Header/Header";
import Dropdown from "../../components/Dropdown/Dropdown";
import ModeDropdown from "../../components/ModeDropdown/ModeDropdown";
import AdminShiftTable from "../../components/AdminShiftTable/AdminShiftTable";
import "./Home.css";
import {
  getCurrentWeek,
  getCurrentYear,
  getDefaultDays,
  getBuiltInStrings,
} from "../../constants";

function Home() {
  const week = getCurrentWeek(0);
  const appliedShiftWeek = getCurrentWeek(2);

  const year = getCurrentYear();

  const [finalShift, setFinalShift] = useState([]);
  const [appliedShift, setAppliedShift] = useState([]);
  const [allShifts, setAllShifts] = useState([]);
  const [selectedOption, setSelectedOption] = useState(true);
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

  const getAllShifts = (week) => {
    api
      .get(`/api/get-shifts-admin/${week}`)
      .then((res) => res.data)
      .then((data) => {
        setAllShifts(data);
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

  const fetchSuccess = () => {
    api.get("/api/get-success-button/").catch((err) => console.log(err));
    window.location.reload();
  };

  useEffect(() => {
    getFinalShift(week);
    getAppliedShift(appliedShiftWeek);
    getAllShifts(week);
    fetchUserDate();
  }, []);

  useEffect(() => {
    getFinalShift(selectedWeekForFinalShifts);
  }, [selectedWeekForFinalShifts]);

  useEffect(() => {
    getAppliedShift(selectedWeekForAppliedShifts);
    getAllShifts(selectedWeekForAppliedShifts);
  }, [selectedWeekForAppliedShifts, selectedOption]);

  const handleSelectWeekForFinalShifts = (week) => {
    setSelectedWeekForFinalShifts(week);
  };

  const handleSelectWeekForAppliedShifts = (week) => {
    setSelectedWeekForAppliedShifts(week);
  };

  const handleDropdownChange = (value) => {
    const option = Boolean(value);
    setSelectedOption(option);
  };

  const createAppliedShift = (e) => {
    e.preventDefault();

    const week = getCurrentWeek(2);
    const actualShift = "0".repeat(21);
    const currDateTime = new Date();
    const year = currDateTime.getFullYear();

    api
      .post("/api/shifts/", {
        week: week,
        year: year,
        applied_shift: application,
        actual_shift: actualShift,
        work_days: getDefaultDays(),
        off_days: getDefaultDays(),
        reserve_days: getDefaultDays(),
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
              {finalShift === undefined || appliedShift === undefined ? (
                <p>{getBuiltInStrings.NO_SCHEDULE_TO_DISPLAY}</p>
              ) : (
                <ShiftPanel
                  schedule={finalShift}
                  appliedSchedule={appliedShift}
                />
              )}
            </>
          ) : (
            <>
              <ModeDropdown onChange={handleDropdownChange} />
              <Dropdown
                year={year}
                finalShifts={false}
                onSelectWeek={handleSelectWeekForAppliedShifts}
              />
              <AdminShiftTable
                shiftsData={allShifts}
                isAcceptedShift={selectedOption}
              />
              <button onClick={fetchSuccess}>Press me</button>
            </>
          )}
        </div>
        <div className="chat-container">
          <form className="chat-form" onSubmit={createAppliedShift}>
            <label htmlFor="content">{getBuiltInStrings.APPLICATION}:</label>
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
