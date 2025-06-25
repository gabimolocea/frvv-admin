import React, { useEffect, useState } from "react";
import { Typography, Box, IconButton, Button } from "@mui/material";
import { ArrowBack } from "@mui/icons-material";
import { Link, useParams } from "react-router-dom";
import { MaterialReactTable } from "material-react-table";
import AxiosInstance from "./Axios";
import { PDFDocument, StandardFonts } from "pdf-lib";
import * as fontkit from "fontkit"; // Import fontkit for custom font support
import PrintIcon from "@mui/icons-material/Print";

const CompetitionDetails = () => {
  const { competitionId } = useParams();
  const [competitionName, setCompetitionName] = useState("");
  const [competitionPlace, setCompetitionPlace] = useState("");
  const [competitionDate, setCompetitionDate] = useState("");
  const [categoriesData, setCategoriesData] = useState([]);
  const [teamsData, setTeamsData] = useState([]);
  const [clubsData, setClubsData] = useState([]);
  const [resolvedData, setResolvedData] = useState({});
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const competitionsResponse = await AxiosInstance.get("/competition/");
        const categoriesResponse = await AxiosInstance.get("/category/");
        const teamsResponse = await AxiosInstance.get("/team/");
        const clubsResponse = await AxiosInstance.get("/club/");

        const competition = competitionsResponse.data.find(
          (comp) => comp.id === parseInt(competitionId)
        );
        setCompetitionName(competition?.name || "Competition Details");
        setCompetitionPlace(competition?.place || "Unknown Place");
        setCompetitionDate(competition?.date || "Unknown Date");

        const filteredCategories = categoriesResponse.data.filter(
          (category) => category.competition === parseInt(competitionId)
        );

        setCategoriesData(filteredCategories);
        setTeamsData(teamsResponse.data);
        setClubsData(clubsResponse.data);
      } catch (error) {
        console.error("Error fetching data:", error);
        setErrorMessage("Failed to fetch data. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [competitionId]);

  const resolveData = async () => {
    const dataMap = {};
    for (const category of categoriesData) {
      const data =
        category.type === "teams"
          ? await Promise.all(
              category.teams.map(async (team) => {
                const teamData = await AxiosInstance.get(`/team/${team.id}`)
                  .then((res) => res.data)
                  .catch((error) => {
                    console.error("Error fetching team data:", error);
                    return null;
                  });

                if (!teamData || !teamData.members) {
                  console.error("No team data or members found for:", team.name);
                  return {
                    id: team.id,
                    athleteOrTeamName: "No members",
                    placement: "Participant",
                    teamMembers: [],
                    team: {
                      group_name: category.group_name || "Unknown Group",
                      category_name: category.name || "Unknown Category",
                      gender: category.gender || "Unknown Gender",
                    },
                  };
                }

                const teamMembers = await Promise.all(
                  teamData.members.map(async (member) => {
                    const athlete = member.athlete;

                    if (!athlete || !athlete.id) {
                      console.error("Invalid athlete data:", athlete);
                      return {
                        athlete: {
                          first_name: "Unknown",
                          last_name: "Athlete",
                        },
                        clubName: "Unknown Club",
                      };
                    }

                    // Fetch the athlete data to get the club ID
                    const athleteData = await AxiosInstance.get(`/athlete/${athlete.id}`)
                      .then((res) => res.data)
                      .catch((error) => {
                        console.error(`Error fetching athlete data for ID ${athlete.id}:`, error);
                        return null;
                      });

                    if (!athleteData || !athleteData.club) {
                      console.error(`No club data found for athlete ID ${athlete.id}`);
                      return {
                        athlete: {
                          first_name: athlete.first_name,
                          last_name: athlete.last_name,
                        },
                        clubName: "Unknown Club",
                      };
                    }

                    // Fetch the club data using the club ID
                    const clubData = await AxiosInstance.get(`/club/${athleteData.club}`)
                      .then((res) => res.data)
                      .catch((error) => {
                        console.error(`Error fetching club data for ID ${athleteData.club}:`, error);
                        return null;
                      });

                    const clubName = clubData?.name || "Unknown Club";
                    return {
                      athlete: {
                        first_name: athlete.first_name,
                        last_name: athlete.last_name,
                      },
                      clubName,
                    };
                  })
                );

                const placement =
                  category.first_place_team?.id === team.id
                    ? "🥇 1st Place"
                    : category.second_place_team?.id === team.id
                    ? "🥈 2nd Place"
                    : category.third_place_team?.id === team.id
                    ? "🥉 3rd Place"
                    : "Participant";

                return {
                  id: team.id,
                  athleteOrTeamName: teamMembers.map(
                    (member) => `${member.athlete.first_name} ${member.athlete.last_name} (${member.clubName})`
                  ).join(" + "), // Combine team members into a single string with "+" between them
                  placement,
                  teamMembers, // Include team members for rendering buttons
                  team: {
                    group_name: category.group_name || "Unknown Group",
                    category_name: category.name || "Unknown Category",
                    gender: category.gender || "Unknown Gender",
                  },
                };
              })
            )
          : category.enrolled_athletes.map((enrollment) => {
              const athlete = enrollment.athlete;
              const clubId = athlete.club; // Get the club ID from the athlete object
              const club = clubsData.find((club) => club.id === clubId); // Find the club using the club ID
              const clubName = club?.name || "Unknown Club";

              return {
                athleteOrTeamName: `${athlete.first_name} ${athlete.last_name} (${clubName})`,
                placement:
                  category.first_place === athlete.id
                    ? "🥇 1st Place"
                    : category.second_place === athlete.id
                    ? "🥈 2nd Place"
                    : category.third_place === athlete.id
                    ? "🥉 3rd Place"
                    : "Participant",
              };
            });

      dataMap[category.id] = data;
    }
    setResolvedData(dataMap);
  };

  useEffect(() => {
    resolveData();
  }, [categoriesData, teamsData, clubsData]);

  const exportToCSV = () => {
    const csvRows = [];
    csvRows.push(`Competition Name: ${competitionName}`);
    csvRows.push(`Total Athletes Enrolled: ${[
      ...new Set(
        categoriesData.flatMap((category) =>
          category.type === "teams"
            ? category.teams.flatMap((teamName) =>
                teamName.split(" + ").map((athleteName) => athleteName.trim())
              )
            : category.enrolled_athletes.map((enrollment) => enrollment.athlete.id)
        )
      ),
    ].length}`);
    csvRows.push(`Total Categories: ${categoriesData.length}`);
    csvRows.push(""); // Add a blank line for separation

    categoriesData.forEach((category) => {
      csvRows.push(`Category: ${category.name}`);
      csvRows.push(`Type: ${category.type}, Gender: ${category.gender}`);
      csvRows.push(""); // Add a blank line for separation

      // Add table headers
      csvRows.push("Athlete/Team Name,Placement");

      const data =
        category.type === "teams"
          ? category.teams.map((teamName) => {
              const placement =
                category.first_place_team_name === teamName
                  ? "🥇 1st Place"
                  : category.second_place_team_name === teamName
                  ? "🥈 2nd Place"
                  : category.third_place_team_name === teamName
                  ? "🥉 3rd Place"
                  : "Participant";

              return {
                athleteOrTeamName: teamName,
                placement,
              };
            })
          : category.enrolled_athletes.map((enrollment) => {
              const athlete = enrollment.athlete;
              return {
                athleteOrTeamName: `${athlete.first_name} ${athlete.last_name}`,
                placement:
                  category.first_place === athlete.id
                    ? "🥇 1st Place"
                    : category.second_place === athlete.id
                    ? "🥈 2nd Place"
                    : category.third_place === athlete.id
                    ? "🥉 3rd Place"
                    : "Participant",
              };
            });

      // Sort data based on placement
      const sortedData = data.sort((a, b) => {
        const placementOrder = {
          "🥇 1st Place": 1,
          "🥈 2nd Place": 2,
          "🥉 3rd Place": 3,
          Participant: 4,
        };
        return placementOrder[a.placement] - placementOrder[b.placement];
      });

      // Add rows for the current category
      sortedData.forEach((row) => {
        csvRows.push(`${row.athleteOrTeamName},${row.placement}`);
      });

      csvRows.push(""); // Add a blank line between categories
    });

    const csvContent = csvRows.join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${competitionName.replace(/\s+/g, "_")}_details.csv`;
    link.click();
  };

  const generateDiplomas = async () => {
    const diplomaTemplates = {
      "🥇 1st Place": "src/assets/diplomas/D_Locul1_CN2025.pdf",
      "🥈 2nd Place": "src/assets/diplomas/D_Locul2_CN2025.pdf", // Path to 2nd place template
      "🥉 3rd Place": "src/assets/diplomas/D_Locul3_CN2025.pdf", // Path to 3rd place template
    };

    categoriesData.forEach(async (category) => {
      const awardedAthletes = category.type === "teams"
        ? category.teams.map((teamName) => {
            const placement =
              category.first_place_team_name === teamName
                ? "🥇 1st Place"
                : category.second_place_team_name === teamName
                ? "🥈 2nd Place"
                : category.third_place_team_name === teamName
                ? "🥉 3rd Place"
                : null;

            return placement ? { name: teamName, placement } : null;
          }).filter(Boolean)
        : category.enrolled_athletes.map((enrollment) => {
            const athlete = enrollment.athlete;
            const placement =
              category.first_place === athlete.id
                ? "🥇 1st Place"
                : category.second_place === athlete.id
                ? "🥈 2nd Place"
                : category.third_place === athlete.id
                ? "🥉 3rd Place"
                : null;

            return placement ? { name: `${athlete.first_name} ${athlete.last_name}`, placement } : null;
          }).filter(Boolean);

      awardedAthletes.forEach(async (awardee) => {
        const templatePath = diplomaTemplates[awardee.placement];
        if (!templatePath) return; // Skip if no template for the placement

        // Fetch the appropriate template PDF
        const templateBytes = await fetch(templatePath)
          .then((res) => {
            console.log("Fetch Response:", res);
            return res.arrayBuffer();
          })
          .catch((error) => {
            console.error("Error fetching template:", error);
          });

        // Load the template PDF
        const pdfDoc = await PDFDocument.load(templateBytes);

        // Get the first page of the template
        const page = pdfDoc.getPages()[0];

        // Add dynamic text to the template
        page.drawText(`Competition: ${competitionName}`, {
          x: 50,
          y: 500,
          size: 16,
          font: await pdfDoc.embedFont(PDFDocument.PDFName.StandardFonts.Helvetica),
        });

        page.drawText(`Category: ${category.name}`, {
          x: 50,
          y: 470,
          size: 14,
          font: await pdfDoc.embedFont(PDFDocument.PDFName.StandardFonts.Helvetica),
        });

        page.drawText(`Awarded to: ${awardee.name}`, {
          x: 50,
          y: 440,
          size: 20,
          font: await pdfDoc.embedFont(StandardFonts.HelveticaBold),
        });

        // Serialize the updated PDF
        const pdfBytes = await pdfDoc.save();

        // Create a Blob and download the updated PDF
        const blob = new Blob([pdfBytes], { type: "application/pdf" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `${category.name.replace(/\s+/g, "_")}_${awardee.name.replace(/\s+/g, "_")}_Diploma.pdf`;
        link.click();
      });
    });
  };

  const generateDiplomasForCategory = async (category) => {
    console.log("Generating diplomas for category:", category.name); // Debugging

    const diplomaTemplates = {
      "1st Place": "/diplomas/D_Locul1_CN2025.pdf",
      "2nd Place": "/diplomas/D_Locul2_CN2025.pdf",
      "3rd Place": "/diplomas/D_Locul3_CN2025.pdf",
    };

    const awardedAthletes = category.type === "teams"
      ? category.teams.map((teamName) => {
          const placement =
            category.first_place_team_name === teamName
              ? "1st Place"
              : category.second_place_team_name === teamName
              ? "2nd Place"
              : category.third_place_team_name === teamName
              ? "3rd Place"
              : null;

          return placement ? { name: teamName, placement } : null;
        }).filter(Boolean)
      : category.enrolled_athletes.map((enrollment) => {
          const athlete = enrollment.athlete;
          const club = clubsData.find((club) => club.id === athlete.club);
          const clubName = club?.name || "Unknown Club";
          const placement =
            category.first_place === athlete.id
              ? "1st Place"
              : category.second_place === athlete.id
              ? "2nd Place"
              : category.third_place === athlete.id
              ? "3rd Place"
              : null;

          return placement
            ? { name: `${athlete.first_name} ${athlete.last_name} (${clubName})`, placement }
            : null;
        }).filter(Boolean);

    console.log("Awarded athletes:", awardedAthletes); // Debugging

    awardedAthletes.forEach(async (awardee) => {
      const templatePath = diplomaTemplates[awardee.placement];
      if (!templatePath) {
        console.error(`No template found for placement: ${awardee.placement}`); // Debugging
        return;
      }

      console.log(`Fetching template for placement: ${awardee.placement}`); // Debugging

      // Fetch the appropriate template PDF
      const templateBytes = await fetch(templatePath)
        .then((res) => res.arrayBuffer())
        .catch((error) => {
          console.error("Error fetching template:", error);
        });

      if (!templateBytes) {
        console.error("Failed to fetch template bytes"); // Debugging
        return;
      }

      // Load the template PDF
      const pdfDoc = await PDFDocument.load(templateBytes);

      // Embed the font
      const font = await pdfDoc.embedFont(StandardFonts.Helvetica);

      
    const textWidthCategory = font.widthOfTextAtSize(`${category.name}`, 20);
    const xPositionCategory = (page.getWidth() - textWidthCategory) / 2;

      page.drawText(`${category.name}`, {
        x: xPositionCategory,
        y: 210,
        size: 20,
        font,
      });


      const textWidth = font.widthOfTextAtSize(`${awardee.name}`, 18);
      const pageWidth = page.getWidth();
      const xPosition = (pageWidth - textWidth) / 2;

      page.drawText(`${awardee.name}`, {
        x: xPosition,
        y: 250,
        size: 20,
        font,
      });

      
      // Serialize the updated PDF
      const pdfBytes = await pdfDoc.save();

      // Create a Blob and download the updated PDF
      const blob = new Blob([pdfBytes], { type: "application/pdf" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `${category.name.replace(/\s+/g, "_")}_${awardee.name.replace(/\s+/g, "_")}_Diploma.pdf`;
      link.click();

      console.log(`Diploma downloaded for ${awardee.name}`); // Debugging
    });
  };

  const generateDiplomaForAwardee = async (category, awardee) => {
    console.log("Awardee data:", awardee); // Debugging
    console.log("Category data:", category); // Debugging
  
    const templatePath = "/diplomas/D_Locul1_CN2025.pdf"; // Example template path
    const templateBytes = await fetch(templatePath)
      .then((res) => res.arrayBuffer())
      .catch((error) => {
        console.error("Error fetching template:", error);
      });
  
    if (!templateBytes) {
      console.error("Failed to fetch template bytes");
      return;
    }
  
    const pdfDoc = await PDFDocument.load(templateBytes);
  
    // Load and embed the custom font
    const fontBytes = await fetch("/fonts/Roboto-ExtraBold.ttf")
      .then((res) => res.arrayBuffer())
      .catch((error) => {
        console.error("Error fetching font:", error);
      });
  
    if (!fontBytes) {
      console.error("Failed to fetch font bytes");
      return;
    }
  
    pdfDoc.registerFontkit(fontkit);
    const customFont = await pdfDoc.embedFont(fontBytes);
  
    const groupWithGender = category.group_name
      ? `${category.group_name} – ${category.gender}`
      : `No Group Assigned – ${category.gender}`;
  
    const page = pdfDoc.getPages()[0];
    const textWidthGroup = customFont.widthOfTextAtSize(groupWithGender, 20);
    const xPositionGroup = (page.getWidth() - textWidthGroup) / 2;
  
    // Write Group name – gender on the diploma
    page.drawText(groupWithGender, {
      x: xPositionGroup,
      y: 170, // Adjust the Y position as needed
      size: 20,
      font: customFont,
    });
  
    const textWidthCategory = customFont.widthOfTextAtSize(`${category.name}`, 20);
    const xPositionCategory = (page.getWidth() - textWidthCategory) / 2;
  
    page.drawText(`${category.name}`, {
      x: xPositionCategory,
      y: 210,
      size: 20,
      font: customFont,
    });
  
    const athleteOrTeamName = awardee.athleteOrTeamName || "Unknown Name"; // Ensure name is defined
    const textWidth = customFont.widthOfTextAtSize(athleteOrTeamName, 18);
    const pageWidth = page.getWidth();
    const xPosition = (pageWidth - textWidth) / 2;
  
    page.drawText(athleteOrTeamName, {
      x: xPosition,
      y: 250,
      size: 20,
      font: customFont,
    });
  
    // Serialize the updated PDF
    const pdfBytes = await pdfDoc.save();
  
    // Ensure category.name and awardee.name are defined
    const categoryName = category.name ? category.name.replace(/\s+/g, "_") : "Unknown_Category";
    const awardeeName = awardee.athleteOrTeamName ? awardee.athleteOrTeamName.replace(/\s+/g, "_") : "Unknown_Awardee";
  
    // Create a Blob and download the updated PDF
    const blob = new Blob([pdfBytes], { type: "application/pdf" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${categoryName}_${awardeeName}_Diploma.pdf`;
    link.click();
  
    console.log(`Diploma downloaded for ${awardee.athleteOrTeamName}`);
  };
  

  const generate_diploma = (category) => {
    const group_name = category.group.name ? category.group.name : "No Group Assigned";
    const diploma_text = `Diploma for ${category.name} - Group: ${group_name}`;
    return diploma_text;
  };

  const generateDiplomasForTeam = async (category, team) => {
    console.log("Team data passed to function:", team); // Debugging

    if (!team.id) {
      console.error("Team ID is undefined");
      return;
    }

    // Fetch the team data from the endpoint
    const teamData = await AxiosInstance.get(`/team/${team.id}`)
      .then((res) => res.data)
      .catch((error) => {
        console.error("Error fetching team data:", error);
        return null;
      });

    if (!teamData || !teamData.members) {
      console.error("No team data or members found for:", team.name);
      return;
    }

    const diplomaTemplatePath = "/diplomas/D_Locul1_CN2025.pdf"; // Example template path

    // Fetch the template PDF
    const templateBytes = await fetch(diplomaTemplatePath)
      .then((res) => res.arrayBuffer())
      .catch((error) => {
        console.error("Error fetching template:", error);
      });

    if (!templateBytes) {
      console.error("Failed to fetch template bytes");
      return;
    }

    // Iterate over team members and create a separate diploma for each athlete
    for (const member of teamData.members) {
      const athlete = member.athlete;

      // Fetch the athlete data to get the club ID
      const athleteData = await AxiosInstance.get(`/athlete/${athlete.id}`)
        .then((res) => res.data)
        .catch((error) => {
          console.error(`Error fetching athlete data for ID ${athlete.id}:`, error);
          return null;
        });

      if (!athleteData || !athleteData.club) {
        console.error(`No club data found for athlete ID ${athlete.id}`);
        continue;
      }

      // Fetch the club data using the club ID
      const clubData = await AxiosInstance.get(`/club/${athleteData.club}`)
        .then((res) => res.data)
        .catch((error) => {
          console.error(`Error fetching club data for ID ${athleteData.club}:`, error);
          return null;
        });

      const clubName = clubData?.name || "Unknown Club";

      // Load the template PDF for each athlete
      const pdfDoc = await PDFDocument.load(templateBytes);

      // Embed the font
      const font = await pdfDoc.embedFont(StandardFonts.Helvetica);

      // Get the first page of the template
      const page = pdfDoc.getPages()[0];

      // Add dynamic text to the diploma
      const athleteName = `${athlete.first_name} ${athlete.last_name}`;
      const groupWithGender = category.group_name
        ? `${category.group_name} – ${category.gender}`
        : `No Group Assigned – ${category.gender}`;

      const textWidthGroup = font.widthOfTextAtSize(groupWithGender, 20);
      const xPositionGroup = (page.getWidth() - textWidthGroup) / 2;

      page.drawText(groupWithGender, {
        x: xPositionGroup,
        y: 170, // Adjust the Y position as needed
        size: 20,
        font,
      });

      const textWidthCategory = font.widthOfTextAtSize(`${category.name}`, 20);
      const xPositionCategory = (page.getWidth() - textWidthCategory) / 2;

      page.drawText(`${category.name}`, {
        x: xPositionCategory,
        y: 210,
        size: 20,
        font,
      });

      const textWidthAthlete = font.widthOfTextAtSize(athleteName, 20);
      const xPositionAthlete = (page.getWidth() - textWidthAthlete) / 2;

      page.drawText(athleteName, {
        x: xPositionAthlete,
        y: 250,
        size: 20,
        font,
      });

      const textWidthClub = font.widthOfTextAtSize(clubName, 18);
      const xPositionClub = (page.getWidth() - textWidthClub) / 2;

      page.drawText(clubName, {
        x: xPositionClub,
        y: 220,
        size: 18,
        font,
      });

      // Serialize the updated PDF
      const pdfBytes = await pdfDoc.save();

      // Create a Blob and download the updated PDF
      const blob = new Blob([pdfBytes], { type: "application/pdf" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `${athleteName.replace(/\s+/g, "_")}_Diploma.pdf`;
      link.click();

      console.log(`Diploma downloaded for team member: ${athleteName}`);
    }
  };

  const generateDiplomaForTeamMember = async (team, teamMember) => {
    console.log("Team data:", team); // Debugging
    console.log("Team member data:", teamMember); // Debugging
  
    if (!teamMember || !teamMember.athlete || !teamMember.athlete.first_name || !teamMember.athlete.last_name) {
      console.error("Invalid team member data:", teamMember);
      return;
    }
  
    const diplomaTemplatePath = "/diplomas/D_Locul1_CN2025.pdf"; // Example template path
  
    // Fetch the template PDF
    const templateBytes = await fetch(diplomaTemplatePath)
      .then((res) => res.arrayBuffer())
      .catch((error) => {
        console.error("Error fetching template:", error);
      });
  
    if (!templateBytes) {
      console.error("Failed to fetch template bytes");
      return;
    }
  
    const pdfDoc = await PDFDocument.load(templateBytes);
  
    // Load and embed the custom font
    const fontBytes = await fetch("/fonts/Roboto-ExtraBold.ttf")
      .then((res) => res.arrayBuffer())
      .catch((error) => {
        console.error("Error fetching font:", error);
      });
  
    if (!fontBytes) {
      console.error("Failed to fetch font bytes");
      return;
    }
  
    pdfDoc.registerFontkit(fontkit);
    const customFont = await pdfDoc.embedFont(fontBytes);
  
    const clubName = teamMember.clubName || "Unknown Club";
  
    // Create a new page for the athlete
    const page = pdfDoc.getPages()[0];
  
    // Add dynamic text to the diploma
    const athleteNameAndClub = `${teamMember.athlete.first_name} ${teamMember.athlete.last_name} – ${clubName}`;
    const textWidthAthleteAndClub = customFont.widthOfTextAtSize(athleteNameAndClub, 24);
    const xPositionAthleteAndClub = (page.getWidth() - textWidthAthleteAndClub) / 2;
  
    page.drawText(athleteNameAndClub, {
      x: xPositionAthleteAndClub,
      y: 250, // Adjust the Y position as needed
      size: 24,
      font: customFont,
    });
  
    const groupWithGender = team?.group_name
      ? `${team.group_name} – ${team.gender || "Unknown Gender"}`
      : `No Group Assigned – ${team?.gender || "Unknown Gender"}`; // Handle undefined group_name and gender
  
    const textWidthGroup = customFont.widthOfTextAtSize(groupWithGender, 20);
    const xPositionGroup = (page.getWidth() - textWidthGroup) / 2;
  
    page.drawText(groupWithGender, {
      x: xPositionGroup,
      y: 170, // Adjust the Y position as needed
      size: 20,
      font: customFont,
    });
  
    const textWidthCategory = customFont.widthOfTextAtSize(`${team?.category_name || "Unknown Category"}`, 20); // Handle undefined category_name
    const xPositionCategory = (page.getWidth() - textWidthCategory) / 2;
  
    page.drawText(`${team?.category_name || "Unknown Category"}`, {
      x: xPositionCategory,
      y: 210,
      size: 20,
      font: customFont,
    });
  
    // Serialize the updated PDF
    const pdfBytes = await pdfDoc.save();
  
    // Generate the file name using the specified format
    const categoryName = team?.category_name ? team.category_name.replace(/\s+/g, "_") : "Unknown_Category";
    const athleteName = `${teamMember.athlete.first_name}_${teamMember.athlete.last_name}`.replace(/\s+/g, "_");
    const clubNameFormatted = clubName.replace(/\s+/g, "_");
    const placement = team.placement || "Participant";
    const yearOfCompetition = new Date().getFullYear(); // Dynamically fetch the current year
    const fileName = `${categoryName}_${athleteName}(${clubNameFormatted})_${placement}_${yearOfCompetition}.pdf`;
  
    // Preview the diploma in the browser
    const blob = new Blob([pdfBytes], { type: "application/pdf" });
    const url = URL.createObjectURL(blob);
    window.open(url, "_blank");
  
    console.log(`Diploma previewed for team member: ${athleteNameAndClub}`);
  };
  

  async function fetchData() {
    const data = await fetch('/api/data');
    console.log(data);
  }

  fetchData();

  const calculateTotalEnrolledAthletes = () => {
    const athleteIds = new Set();

    categoriesData.forEach((category) => {
      if (category.type === "teams") {
        category.teams.forEach((team) => {
          team.members.forEach((member) => {
            athleteIds.add(member.athlete.id);
          });
        });
      } else {
        category.enrolled_athletes.forEach((enrollment) => {
          athleteIds.add(enrollment.athlete.id);
        });
      }
    });

    return athleteIds.size; // Count unique athlete IDs
  };

  if (loading) {
    return <Typography>Loading competition details...</Typography>;
  }

  if (errorMessage) {
    return <Typography color="error">{errorMessage}</Typography>;
  }

  if (categoriesData.length === 0) {
    return (
      <Typography variant="h6" sx={{ padding: 2 }}>
        No categories found for this competition.
      </Typography>
    );
  }

  return (
    <Box>
      {/* Competition Information */}
      <Box sx={{ marginBottom: 4, padding: 2, border: "1px solid black", borderRadius: 1 }}>
        <Typography variant="h5">{competitionName}</Typography>
        <Typography variant="subtitle1">Place: {competitionPlace}</Typography>
        <Typography variant="subtitle1">Date: {competitionDate}</Typography>
        <Typography variant="subtitle1">
          Total Enrolled Athletes: {calculateTotalEnrolledAthletes()}
        </Typography>
        <Typography variant="subtitle1">Total Categories: {categoriesData.length}</Typography>
      </Box>

      {/* Back Arrow */}
      <Box sx={{ display: "flex", alignItems: "center", marginBottom: 2 }}>
        <IconButton component={Link} to="/competitions" sx={{ marginRight: 1 }}>
          <ArrowBack />
        </IconButton>
      </Box>

      {categoriesData.map((category) => {
        const columns = [
          {
            accessorKey: "athleteOrTeamName",
            header: "Athlete/Team Name",
          },
          {
            accessorKey: "placement",
            header: "Placement",
          },
          {
            accessorKey: "actions",
            header: "Actions",
            Cell: ({ row }) => {
              const awardee = row.original;
              if (category.type === "teams") {
                return awardee.teamMembers.map((teamMember, index) => (
                  <IconButton
                    key={index}
                    color="secondary"
                    onClick={() => generateDiplomaForTeamMember(awardee.team, teamMember)}
                    sx={{ marginTop: 1 }}
                  >
                    <PrintIcon />
                  </IconButton>
                ));
              } else {
                return (
                  <IconButton onClick={() => generateDiplomaForAwardee(category, awardee)}>
                    <PrintIcon />
                  </IconButton>
                );
              }
            },
          },
        ];

        const data = resolvedData[category.id] || [];

        return (
          <Box
            key={category.id}
            sx={{
              marginBottom: 4,
              border: "1px solid black",
              borderRadius: 1,
            }}
          >
            <Box
              sx={{
                marginBottom: 0,
                backgroundColor: "#f5f5f5",
                padding: 2,
                borderBottom: "1px solid black",
              }}
            >
              <Typography variant="h6">{category.name}</Typography>
              <Typography variant="subtitle1">
                Type: {category.type}, Gender: {category.gender}
              </Typography>
              <Typography variant="subtitle1">
                Enrolled {category.type === "teams" ? "Teams" : "Athletes"}:{" "}
                {category.type === "teams" ? category.teams.length : category.enrolled_athletes.length}
              </Typography>
            </Box>

            <MaterialReactTable
              columns={columns}
              data={data} // Use resolved data
              enableColumnFilters={false}
              enableGlobalFilter={false}
              enableColumnOrdering={false}
              enableFullScreenToggle={false}
              enablePagination={false}
              enableSorting={false}
              enableRowActions={false}
              enableDensityToggle={false}
              enableHiding={false}
              enableBottomToolbar={false}
              enableTopToolbar={false}
              enableRowSelection={false}
              enableColumnActions={false}
              muiTableBodyCellProps={({ cell }) => ({
                sx: {
                  fontWeight: cell.column.id === "placement" && cell.getValue()?.includes("Place") ? "bold" : "normal",
                },
              })}
            />
          </Box>
        );
      })}
    </Box>
  );
};

export default CompetitionDetails;