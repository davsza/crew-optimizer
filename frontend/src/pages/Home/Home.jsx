import { useState, useEffect } from "react";
import api from "../../api";
import RosterPanel from "../../components/RosterPanel/RosterPanel";
import Header from "../../components/Header/Header";
import Dropdown from "../../components/Dropdown/Dropdown";
import ModeDropdown from "../../components/ModeDropdown/ModeDropdown";
import AdminRosterTable from "../../components/AdminRosterTable/AdminRosterTable";
import Message from "../../components/Message/Message";
import "./Home.css";
import {
  getCurrentWeek,
  getCurrentYear,
  getBuiltInStrings,
} from "../../constants";

function Home() {
  const week_number = getCurrentWeek(0);
  const appliedRosterWeek = getCurrentWeek(2);

  const year = getCurrentYear();

  const [schedule, setSchedule] = useState([]);
  const [application, setApplication] = useState([]);
  const [allOfSchedules, setAllOfSchedules] = useState([]);
  const [selectedOption, setSelectedOption] = useState(true);
  const [selectedWeekForSchedule, setSelectedWeekForSchedule] =
    useState(week_number);
  const [selectedWeekForApplication, setSelectedWeekForApplication] =
    useState(appliedRosterWeek);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [userGroup, setUserGroup] = useState("");
  const [userName, setUserName] = useState("");

  const getSchedule = (week_number) => {
    api
      .get(`/api/rosters/${week_number}`)
      .then((res) => res.data)
      .then((data) => {
        setSchedule(data[0]);
      })
      .catch((err) => alert(err));
  };

  const getApplication = (week_number) => {
    api
      .get(`/api/rosters/${week_number}`)
      .then((res) => res.data)
      .then((data) => {
        setApplication(data[0]);
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

  const getAllRosters = (week_number) => {
    api
      .get(`/api/get-rosters-admin/${week_number}`)
      .then((res) => res.data)
      .then((data) => {
        setAllOfSchedules(data);
      })
      .catch((err) => alert(err));
  };

  const getUserData = () => {
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
    getSchedule(week_number);
    getApplication(appliedRosterWeek);
    getAllRosters(week_number);
    getUserData();
    getMessages();
  }, []);

  useEffect(() => {
    getSchedule(selectedWeekForSchedule);
  }, [selectedWeekForSchedule]);

  useEffect(() => {
    getApplication(selectedWeekForApplication);
    getAllRosters(selectedWeekForApplication);
  }, [selectedWeekForApplication, selectedOption]);

  const handleSelectWeekForFinalRosters = (week_number) => {
    setSelectedWeekForSchedule(week_number);
  };

  const handleSelectWeekForAppliedRosters = (week_number) => {
    setSelectedWeekForApplication(week_number);
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
          console.log("Failed to make a roster");
        }
        getMessages();
        getApplication(appliedRosterWeek);
        getAllRosters(appliedRosterWeek);
      })
      .catch((err) => alert(err));

    setMessage("");
  };

  return (
    <div>
      <Header userName={userName}></Header>
      <div className="container">
        <div className="schedule-container">
          {userGroup !== "Supervisor" ? (
            <>
              <div className="dropdown-container">
                <Dropdown
                  year={year}
                  finalRosters={true}
                  onSelectWeek={handleSelectWeekForFinalRosters}
                />
                <Dropdown
                  year={year}
                  finalRosters={false}
                  onSelectWeek={handleSelectWeekForAppliedRosters}
                />
              </div>
              {schedule === undefined || application === undefined ? (
                <p>{getBuiltInStrings.NO_SCHEDULE_TO_DISPLAY}</p>
              ) : (
                <div className="table-container">
                  <RosterPanel
                    schedule={schedule}
                    appliedSchedule={application}
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
                  finalRosters={false}
                  onSelectWeek={handleSelectWeekForAppliedRosters}
                />
              </div>
              <div className="table-container">
                <AdminRosterTable
                  rostersData={allOfSchedules}
                  isAcceptedRoster={selectedOption}
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
