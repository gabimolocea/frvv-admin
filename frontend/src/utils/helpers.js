export const getClubNameForAthlete = (athleteId, athletesData, clubsData) => {
  if (!athleteId) {
    console.warn("Athlete ID is undefined");
    return "Unknown Club";
  }

  const athlete = athletesData.find((athlete) => athlete.id === athleteId);
  if (!athlete || !athlete.club) {
    return "Unknown Club";
  }
  const club = clubsData.find((club) => club.id === athlete.club);
  return club ? club.name : "Unknown Club";
};