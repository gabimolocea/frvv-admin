import React, { useState, useEffect } from "react";
import { Box, FormControl, Button } from "@mui/material";
import { useNavigate, useParams } from "react-router-dom";
import AxiosInstance from "./Axios";
import DeleteDialog from "./DeleteDialog"; // Import the global DeleteDialog component
import TextForm from "./forms/TextForm";
import SelectForm from "./forms/SelectForm";
import { useFormik } from "formik";
import * as Yup from "yup";
import MyMessage from "./forms/Message";

const Edit = () => {
  const { id } = useParams(); // Get the club ID from the route
  const navigate = useNavigate();
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false); // State for delete dialog
  const [message, setMessage] = useState("");
  const [city, setCity] = useState([]);
  const [competition, setCompetition] = useState([]);
  const [myData, setMyData] = useState([]);

  const GetData = async () => {
    AxiosInstance.get("city/").then((res) => {
      setCity(res.data);
    });

    AxiosInstance.get(`club/${id}/`).then((res) => {
      setMyData(res.data); // Populate myData with the fetched club data
    });

    AxiosInstance.get("competition/").then((res) => {
      setCompetition(res.data);
    });
  };

  useEffect(() => {
    GetData();
  }, []);

  const validationSchema = Yup.object({
    name: Yup.string().required("Club name is required"),
    city: Yup.string().required("City is required"),
    address: Yup.string().required("Address is required"),
    mobile_number: Yup.string()
      .matches(/^[0-9]+$/, "Mobile number must be digits")
      .required("Mobile number is required"),
    website: Yup.string()
      .matches(
        /^(http:\/\/)[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+$/,
        "Website must start with 'http://' and be a valid URL"
      )
      .required("Website is required"),
  });

  const formik = useFormik({
    initialValues: {
      name: myData.name || "", // Use empty string as fallback
      city: myData.city ? myData.city.id : "",
      address: myData.address || "",
      coach: myData.coach || "",
      mobile_number: myData.mobile_number || "",
      website: myData.website || "",
    },
    enableReinitialize: true, // This allows the form to reinitialize when myData changes
    validationSchema: validationSchema,

    onSubmit: (values) => {
      const payload = {
        ...values,
        city: values.city, // Send only the city ID
      };

      console.log("Submitting Payload:", payload); // Debugging: Log the payload

      AxiosInstance.put(`club/${id}/`, payload)
        .then(() => {
          setMessage(
            <MyMessage
              messageText={"You successfully edited the club!"}
              messageColor={"green"}
            />
          );
          setTimeout(() => {
            navigate("/clubs");
          }, 2000);
        })
        .catch((error) => {
          console.error("Error updating the club:", error); // Handle errors
        });
    },
  });

  const handleDeleteClub = async () => {
    try {
      await AxiosInstance.delete(`club/${id}/`);
      console.log("Deleted club:", id);
      setMessage("Club deleted successfully!");
      setTimeout(() => {
        navigate("/clubs"); // Redirect to the clubs page after deletion
      }, 2000);
    } catch (error) {
      console.error("Error deleting club:", error);
    }
  };

  const handleCancel = () => {
    navigate(-1); // Navigate back to the previous page
  };

  return (
    <div>
      <form onSubmit={formik.handleSubmit}>
        {message && <p>{message}</p>}
        <Box>
          <FormControl
            sx={{ display: "flex", flexWrap: "wrap", width: "100%", gap: "1rem" }}
          >
            <TextForm
              label={"Club name"}
              name="name"
              value={formik.values.name}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.name && Boolean(formik.errors.name)}
              helperText={formik.touched.name && formik.errors.name}
            />

            <SelectForm
              label={"City"}
              options={city}
              name="city"
              value={formik.values.city}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.city && Boolean(formik.errors.city)}
              helperText={formik.touched.city && formik.errors.city}
            />

            <TextForm
              label={"Address"}
              name="address"
              value={formik.values.address}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.address && Boolean(formik.errors.address)}
              helperText={formik.touched.address && formik.errors.address}
            />

            <TextForm
              label={"Mobile number"}
              name="mobile_number"
              value={formik.values.mobile_number}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.mobile_number && Boolean(formik.errors.mobile_number)}
              helperText={formik.touched.mobile_number && formik.errors.mobile_number}
            />

            <TextForm
              label={"Website"}
              name="website"
              value={formik.values.website}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              error={formik.touched.website && Boolean(formik.errors.website)}
              helperText={formik.touched.website && formik.errors.website}
            />

            <Button type="submit" variant="contained" size="large">
              Save the data
            </Button>

            <Button
              variant="contained"
              color="error"
              size="large"
              onClick={() => setOpenDeleteDialog(true)} // Open the delete dialog
            >
              Delete Club
            </Button>

            <Button
              variant="outlined"
              color="secondary"
              size="large"
              onClick={handleCancel} // Navigate back without saving
            >
              Cancel
            </Button>
          </FormControl>
        </Box>
      </form>

      {/* Use the global DeleteDialog component */}
      <DeleteDialog
        open={openDeleteDialog}
        onClose={() => setOpenDeleteDialog(false)}
        onConfirm={handleDeleteClub}
        itemName={`the club "${myData.name}"`}
      />
    </div>
  );
};

export default Edit;
