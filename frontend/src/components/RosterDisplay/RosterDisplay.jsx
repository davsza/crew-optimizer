import { getRosterDisplayParameters } from "../../constants";
import "./RosterDisplay.css";
import { getBuiltInStrings } from "../../constants";

const RosterDisplay = ({
  scheduleOfTheDay,
  appliedScheduleOfTheDay,
  highlighted,
  workDays,
  offDays,
  reserveDays,
  vacation,
  sickness,
  reserveCallIn,
  published,
  day,
  application,
}) => {
  return (
    <div
      className={`outer ${highlighted ? "highlighted" : ""} ${
        reserveCallIn[day] === "1" ? "reserveCallIn" : ""
      }`}
    >
      {(workDays[day] === "1" || application) && vacation[day] !== "1" ? (
        scheduleOfTheDay.map((roster, index) => {
          const { from, to, applicationForSchedule, style } =
            getRosterDisplayParameters(roster, index, appliedScheduleOfTheDay);
          return (
            <div
              key={index}
              className={`inner ${
                applicationForSchedule === "1" && !application
                  ? "application"
                  : ""
              }`}
              style={style}
            >
              {from} - {to}
            </div>
          );
        })
      ) : reserveCallIn[day] === "1" ? (
        scheduleOfTheDay.map((roster, index) => {
          const { from, to, applicationForSchedule, style } =
            getRosterDisplayParameters(roster, index, appliedScheduleOfTheDay);
          return (
            <div
              key={index}
              className={`inner ${
                applicationForSchedule === "1" && !application
                  ? "application"
                  : ""
              }`}
              style={style}
            >
              {from} - {to}
            </div>
          );
        })
      ) : sickness[day] === "1" ? (
        <div
          className="inner"
          style={{
            bottom: "0",
            left: "0",
            right: "0",
            width: "90%",
            margin: "auto",
            backgroundColor: "orange",
          }}
        >
          {getBuiltInStrings.SICKNESS}
        </div>
      ) : vacation[day] === "1" ? (
        <div
          className="inner"
          style={{
            bottom: "0",
            left: "0",
            right: "0",
            width: "90%",
            margin: "auto",
            backgroundColor: "purple",
          }}
        >
          {getBuiltInStrings.VACATION_CLAIM}
        </div>
      ) : offDays[day] === "1" ? (
        <div
          className="inner"
          style={{
            bottom: "0",
            left: "0",
            right: "0",
            width: "90%",
            margin: "auto",
            backgroundColor: "green",
          }}
        >
          {getBuiltInStrings.DAY_OFF}
        </div>
      ) : reserveDays[day] === "1" ? (
        <div
          className="inner"
          style={{
            bottom: "0",
            left: "0",
            right: "0",
            width: "90%",
            margin: "auto",
            backgroundColor: "blue",
          }}
        >
          {getBuiltInStrings.RESERVE}
        </div>
      ) : (
        <div>{getBuiltInStrings.NO_SCHEDULE_TO_DISPLAY}</div>
      )}
    </div>
  );
};

export default RosterDisplay;
