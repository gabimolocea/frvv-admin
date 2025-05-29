import React, { useEffect, useState } from "react";
import { Box, Button, Typography, FormControl, Snackbar, Alert } from "@mui/material";
import { useFormik } from "formik";
import * as Yup from "yup";
import { useNavigate, useParams } from "react-router-dom";
import AxiosInstance from "./Axios";
import TextForm from "./forms/TextForm";
import SelectForm from "./forms/SelectForm";
import { DatePicker, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";
import DeleteDialog from "./DeleteDialog"; // Import your existing DeleteDialog component

const EditAthlete = () => {
  const { id } = useParams(); // Get athlete ID from URL
  const navigate = useNavigate();
  const [clubs, setClubs] = useState([]);
  const [cities, setCities] = useState([]);
  const [grades, setGrades] = useState([]);
  const [roles, setRoles] = useState([]);
  const [titles, setTitles] = useState([]);
  const [initialValues, setInitialValues] = useState(null);
  const [successMessage, setSuccessMessage] = useState(""); // Success message state
  const [errorMessage, setErrorMessage] = useState(""); // Error message state
  const [openDialog, setOpenDialog] = useState(false); // State for DeleteDialog

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch athlete data
        const athleteResponse = await AxiosInstance.get(`athlete/${id}/`);
        const athleteData = athleteResponse.data;

        // Fetch clubs, cities, grades, roles, and titles
        const clubsResponse = await AxiosInstance.get("club/");
        const citiesResponse = await AxiosInstance.get("city/");
        const gradesResponse = await AxiosInstance.get("grade/");
        const rolesResponse = await AxiosInstance.get("federation-role/");
        const titlesResponse = await AxiosInstance.get("title/");

        setClubs(clubsResponse.data.map((club) => ({ id: club.id, name: club.name })));
        setCities(citiesResponse.data.map((city) => ({ id: city.id, name: city.name })));
        setGrades(gradesResponse.data.map((grade) => ({ id: grade.id, name: grade.name })));
        setRoles(rolesResponse.data.map((role) => ({ id: role.id, name: role.name })));
        setTitles(titlesResponse.data.map((title) => ({ id: title.id, name: title.name })));

        // Set initial form values
        setInitialValues({
          first_name: athleteData.first_name || "",
          last_name: athleteData.last_name || "",
          date_of_birth: athleteData.date_of_birth ? new Date(athleteData.date_of_birth) : null,
          city: athleteData.city || "",
          mobile_number: athleteData.mobile_number || "",
          club: athleteData.club || "",
          registered_date: athleteData.registered_date ? new Date(athleteData.registered_date) : null,
          expiration_date: athleteData.expiration_date ? new Date(athleteData.expiration_date) : null,
          is_coach: athleteData.is_coach || false,
          federation_role: athleteData.federation_role || "",
          title: athleteData.title || "",
          current_grade: athleteData.current_grade || "",
        });
      } catch (error) {
        console.error("Error fetching athlete data:", error);
      }
    };

    fetchData();
  }, [id]);

  const formik = useFormik({
    initialValues: initialValues || {
      first_name: "",
      last_name: "",
      date_of_birth: null,
      city: "",
      mobile_number: "",
      club: "",
      registered_date: null,
      expiration_date: null,
      is_coach: false,
      federation_role: "",
      title: "",
      current_grade: "",
    },
    enableReinitialize: true, // Allow form to reinitialize when initialValues change
    validationSchema: Yup.object({
      first_name: Yup.string().required("First name is required"),
      last_name: Yup.string().required("Last name is required"),
      date_of_birth: Yup.date().required("Date of birth is required"),
      city: Yup.string().required("City is required"),
    }),
    onSubmit: async (values) => {
      const payload = {
        ...values,
        date_of_birth: values.date_of_birth?.toISOString().split("T")[0],
        registered_date: values.registered_date?.toISOString().split("T")[0],
        expiration_date: values.expiration_date?.toISOString().split("T")[0],
      };

      try {
        await AxiosInstance.put(`athlete/${id}/`, payload);
        setSuccessMessage("Athlete updated successfully!"); // Set success message
        navigate("/athletes"); // Redirect to the athletes list
      } catch (error) {
        console.error("Error updating athlete:", error);
        setErrorMessage("Failed to update athlete. Please try again."); // Set error message
      }
    },
  });

  const handleDelete = async () => {
    try {
      await AxiosInstance.delete(`athlete/${id}/`);
      setSuccessMessage("Athlete deleted successfully!"); // Set success message
      navigate("/athletes"); // Redirect to the athletes list
    } catch (error) {
      console.error("Error deleting athlete:", error);
      setErrorMessage("Failed to delete athlete. Please try again."); // Set error message
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box
        component="form"
        onSubmit={formik.handleSubmit}
    
      >
        

        {/* Personal Information Section */}
        <Typography variant="h6" sx={{ marginBottom: 2 }}>
          Personal Information
        </Typography>
        <FormControl sx={{ display: "flex", flexWrap: "wrap", width: "100%", gap: "1rem" }}>
          <TextForm
            label="First Name *"
            name="first_name"
            value={formik.values.first_name}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.first_name && Boolean(formik.errors.first_name)}
            helperText={formik.touched.first_name && formik.errors.first_name}
          />
          <TextForm
            label="Last Name *"
            name="last_name"
            value={formik.values.last_name}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.last_name && Boolean(formik.errors.last_name)}
            helperText={formik.touched.last_name && formik.errors.last_name}
          />
          <DatePicker
            label="Date of Birth *"
            value={formik.values.date_of_birth}
            onChange={(value) => formik.setFieldValue("date_of_birth", value)}
            renderInput={(params) => (
              <TextForm
                {...params}
                name="date_of_birth"
                error={formik.touched.date_of_birth && Boolean(formik.errors.date_of_birth)}
                helperText={formik.touched.date_of_birth && formik.errors.date_of_birth}
              />
            )}
          />
          <SelectForm
            label="City *"
            name="city"
            options={cities}
            value={formik.values.city}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.city && Boolean(formik.errors.city)}
            helperText={formik.touched.city && formik.errors.city}
          />
          <TextForm
            label="Mobile Number"
            name="mobile_number"
            value={formik.values.mobile_number}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
          />
        </FormControl>

        {/* Club Information Section */}
        <Typography variant="h6" sx={{ marginTop: 4, marginBottom: 2 }}>
          Club Information
        </Typography>
        <FormControl sx={{ display: "flex", flexWrap: "wrap", width: "100%", gap: "1rem" }}>
          <SelectForm
            label="Club"
            name="club"
            options={clubs}
            value={formik.values.club}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
          />
          <DatePicker
            label="Registered Date"
            value={formik.values.registered_date}
            onChange={(value) => formik.setFieldValue("registered_date", value)}
            renderInput={(params) => (
              <TextForm
                {...params}
                name="registered_date"
              />
            )}
          />
          <DatePicker
            label="Expiration Date"
            value={formik.values.expiration_date}
            onChange={(value) => formik.setFieldValue("expiration_date", value)}
            renderInput={(params) => (
              <TextForm
                {...params}
                name="expiration_date"
              />
            )}
          />
          <SelectForm
            label="Is Coach"
            name="is_coach"
            options={[
              { id: true, name: "Yes" },
              { id: false, name: "No" },
            ]}
            value={formik.values.is_coach}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
          />
        </FormControl>

        {/* Federation Role and Title Section */}
        <Typography variant="h6" sx={{ marginTop: 4, marginBottom: 2 }}>
          Federation Role and Title
        </Typography>
        <FormControl sx={{ display: "flex", flexWrap: "wrap", width: "100%", gap: "1rem" }}>
          <SelectForm
            label="Federation Role"
            name="federation_role"
            options={roles}
            value={formik.values.federation_role}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
          />
          <SelectForm
            label="Title"
            name="title"
            options={titles}
            value={formik.values.title}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
          />
          <SelectForm
            label="Current Grade"
            name="current_grade"
            options={grades}
            value={formik.values.current_grade}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
          />
        </FormControl>

        <Box sx={{ display: "flex", flexDirection: "column", gap: 2, marginTop: 4, width: "100%" }}>
          <Button
            variant="contained"
            color="primary"
            size="large"
            fullWidth
            type="submit"
          >
            Update Athlete
          </Button>
          <Button
            variant="contained"
            color="error"
            size="large"
            fullWidth
            onClick={() => setOpenDialog(true)} // Open DeleteDialog
          >
            Delete Athlete
          </Button>
          <Button
            variant="outlined"
            color="secondary"
            size="large"
            fullWidth
            onClick={() => navigate("/athletes")}
          >
            Cancel
          </Button>
        </Box>

        {/* DeleteDialog */}
            <DeleteDialog
              open={openDialog}
              onClose={() => setOpenDialog(false)}
              onConfirm={handleDelete}
              itemName={`${formik.values.first_name} ${formik.values.last_name}`}
            />

            {/* Snackbar for success and error messages */}
        <Snackbar
          open={!!successMessage}
          autoHideDuration={3000}
          onClose={() => setSuccessMessage("")}
        >
          <Alert onClose={() => setSuccessMessage("")} severity="success" sx={{ width: "100%" }}>
            {successMessage}
          </Alert>
        </Snackbar>
        <Snackbar
          open={!!errorMessage}
          autoHideDuration={3000}
          onClose={() => setErrorMessage("")}
        >
          <Alert onClose={() => setErrorMessage("")} severity="error" sx={{ width: "100%" }}>
            {errorMessage}
          </Alert>
        </Snackbar>
      </Box>
    </LocalizationProvider>
  );
};

export default EditAthlete;
