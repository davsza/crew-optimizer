export const ACCESS_TOKEN = "access";
export const REFRESH_TOKEN = "refresh";
export const MONTHS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];
export const DAYS = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];

export const getCurrentWeek = (additionalWeeks) => {
  const now = new Date();
  const yearStart = new Date(now.getFullYear(), 0, 0);
  const diff = now - yearStart;
  const oneWeek = 1000 * 60 * 60 * 24 * 7;
  let weekNumber = Math.floor(diff / oneWeek) + 1;
  const currentDay = now.getDay();
  if (currentDay <= 3) {
    weekNumber -= 1;
  } 
  weekNumber += additionalWeeks;
  return weekNumber;
};
