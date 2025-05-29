import React, { useState, useEffect } from "react";
import { Box, Button, Typography, FormControl } from "@mui/material";
import { useFormik } from "formik";
import * as Yup from "yup";
import AxiosInstance from "./Axios";
import { useNavigate } from "react-router-dom";
import TextForm from "./forms/TextForm";
import SelectForm from "./forms/SelectForm";
import { DatePicker } from "@mui/x-date-pickers";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDateFns } from "@mui/x-date-pickers/AdapterDateFns";

const CreateAthlete = () => {
  const [clubs, setClubs] = useState([]);
  const [cities, setCities] = useState([]);
  const [grades, setGrades] = useState([]);
  const [roles, setRoles] = useState([]);
  const [titles, setTitles] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const clubsResponse = await AxiosInstance.get("club/");
        setClubs(clubsResponse.data.map((club) => ({ id: club.id, name: club.name })));
      } catch (error) {
        console.error("Error fetching clubs:", error);
        setClubs([]);
      }

      try {
        const citiesResponse = await AxiosInstance.get("city/");
        setCities(citiesResponse.data.map((city) => ({ id: city.id, name: city.name })));
      } catch (error) {
        console.error("Error fetching cities:", error);
        setCities([]);
      }

      try {
        const gradesResponse = await AxiosInstance.get("grade/");
        setGrades(gradesResponse.data.map((grade) => ({ id: grade.id, name: grade.name })));
      } catch (error) {
        console.error("Error fetching grades:", error);
        setGrades([]);
      }

      try {
        const rolesResponse = await AxiosInstance.get("federation-role/");
        setRoles(rolesResponse.data.map((role) => ({ id: role.id, name: role.name })));
      } catch (error) {
        console.error("Error fetching roles:", error);
        setRoles([]);
      }

      try {
        const titlesResponse = await AxiosInstance.get("title/");
        setTitles(titlesResponse.data.map((title) => ({ id: title.id, name: title.name })));
      } catch (error) {
        console.error("Error fetching titles:", error);
        setTitles([]);
      }
    };
    fetchData();
  }, []);

  const formik = useFormik({
    initialValues: {
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

      console.log("Submitting athlete data:", payload);

      try {
        await AxiosInstance.post("athlete/", payload);
        console.log("Athlete created successfully:", payload);
        navigate("/athletes");
      } catch (error) {
        console.error("Error creating athlete:", error);
        console.error("Backend response:", error.response?.data);
      }
    },
  });

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

        <Box sx={{ display: "flex", justifyContent: "space-between", marginTop: 4, width: "100%" }}>
          <Button variant="outlined" color="secondary" onClick={() => navigate("/athletes")}>
            Cancel
          </Button>
          <Button type="submit" variant="contained" color="primary">
            Create Athlete
          </Button>
        </Box>
      </Box>
    </LocalizationProvider>
  );
};

export default CreateAthlete;