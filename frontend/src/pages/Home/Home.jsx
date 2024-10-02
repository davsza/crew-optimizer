import { useState, useEffect } from "react";
import api from "../../api";
import ShiftPanel from "../../components/ShiftPanel/ShitPanel";
import Header from "../../components/Header/Header";
import Dropdown from "../../components/Dropdown/Dropdown";
import ModeDropdown from "../../components/ModeDropdown/ModeDropdown";
import AdminShiftTable from "../../components/AdminShiftTable/AdminShiftTable";
import Message from "../../components/Message/Message";
import "./Home.css";
import {
  getCurrentWeek,
  getCurrentYear,
  getBuiltInStrings,
  getAdminTableHeader,
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
  const [message, setMessage] = useState("");
  const [userGroup, setUserGroup] = useState("");
  const [userName, setUserName] = useState("");
  const [messages, setMessages] = useState([]);

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

  const getMessages = () => {
    api
      .get("/api/message/")
      .then((res) => res.data)
      .then((data) => {
        setMessages(data);
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
    getMessages();
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

  const createMessage = (e) => {
    e.preventDefault();

    const currDateTime = new Date();

    api
      .post("/api/agent/", {
        text: message,
        date: currDateTime,
        sent_by_user: true,
      })
      .then((res) => {
        if (res.status === 201) {
          console.log("Message sent");
        } else {
          console.log("Failed to make a shift");
        }
        getMessages();
        getAppliedShift(appliedShiftWeek);
        getAllShifts(appliedShiftWeek);
      })
      .catch((err) => alert(err));

    setMessage("");
  };

  return (
    <div>
      <Header userName={userName}></Header>
      <button onClick={fetchSuccess}>
        {getBuiltInStrings.GENERATE_SHIFTS}
      </button>
      <div className="container">
        <div className="schedule-container">
          {userGroup !== "Supervisor" ? (
            <>
              <div className="dropdown-container">
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
              </div>
              {finalShift === undefined || appliedShift === undefined ? (
                <p>{getBuiltInStrings.NO_SCHEDULE_TO_DISPLAY}</p>
              ) : (
                <div className="table-container">
                  <ShiftPanel
                    schedule={finalShift}
                    appliedSchedule={appliedShift}
                  />
                </div>
              )}
            </>
          ) : (
            <>
              <div className="dropdown-container">
                <ModeDropdown onChange={handleDropdownChange} />
                <Dropdown
                  year={year}
                  finalShifts={false}
                  onSelectWeek={handleSelectWeekForAppliedShifts}
                />
              </div>
              <div className="table-container">
                <AdminShiftTable
                  shiftsData={allShifts}
                  isAcceptedShift={selectedOption}
                />
              </div>
            </>
          )}
        </div>
        <div className="chat-container">
          <div className="chat-area">
            {messages.map((message, index) => (
              <Message
                text={message.text}
                date={message.date}
                isSentByUser={message.sent_by_user}
                index={index}
              ></Message>
            ))}
          </div>
          <form className="chat-form" onSubmit={createMessage}>
            <textarea
              className="chat-input"
              id="content"
              name="content"
              required
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            ></textarea>
            <br />
            <input
              className="chat-input-button"
              type="submit"
              value="Submit request"
            ></input>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Home;
