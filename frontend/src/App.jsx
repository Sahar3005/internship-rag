import { useState } from "react";
import {
  Upload,
  FileText,
  Search,
  MapPin,
  Briefcase,
  Clock,
  Sparkles,
  CheckCircle2,
} from "lucide-react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile);
      setResults([]);
      setError("");
    } else {
      alert("Please upload a PDF resume.");
    }
  };

  const findMatches = async () => {
    if (!file) return;

    setLoading(true);
    setError("");
    setResults([]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        "https://internship-rag-2.onrender.com/recommend-resume",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong.");
      }

      setResults(data.matches || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">

      {/* Navbar */}
      <nav className="navbar">
        <div className="logo">
          <span>InternMatch AI</span>
        </div>

        <div className="nav-links">
          <span>How It Works</span>
          <span>About</span>
        </div>
      </nav>

      {/* Hero */}
      <section className="hero">
        <div className="hero-content">

          <div className="badge">
            AI-Powered Internship Matching
          </div>

          <h1>
            Find Internships That
            <span>Match Your Skills</span>
          </h1>

          <p>
            Upload your resume and let our AI analyze your skills, education,
            projects, and experience to find the most relevant internships.
          </p>

          {/* Upload Box */}
          <div className="upload-box">

            <input
              type="file"
              id="resume"
              accept=".pdf"
              onChange={handleFileChange}
              hidden
            />

            <label htmlFor="resume" className="upload-content">

              <div className="upload-icon">
                <Upload size={30} />
              </div>

              {file ? (
                <>
                  <h3>{file.name}</h3>
                  <p>Resume selected successfully</p>
                </>
              ) : (
                <>
                  <h3>Upload your resume</h3>
                  <p>
                    Drag & drop your PDF here or click to browse
                  </p>
                </>
              )}

              <span className="pdf-info">
                <FileText size={15} />
                PDF only
              </span>

            </label>
          </div>

          {/* Match Button */}
          <button
            className="match-btn"
            disabled={!file || loading}
            onClick={findMatches}
          >
            <Search size={19} />

            {loading
              ? "Analyzing Resume..."
              : "Find Matching Internships"}
          </button>

          {/* Error */}
          {error && (
            <p className="error-message">
              {error}
            </p>
          )}

        </div>
      </section>

      {/* Features */}
      <section className="features">

        <div className="feature">
          <CheckCircle2 />

          <div>
            <h3>Resume Analysis</h3>
            <p>
              Extract skills, education, projects and experience.
            </p>
          </div>
        </div>

        <div className="feature">
          <Sparkles />

          <div>
            <h3>AI Matching</h3>
            <p>
              Semantic matching using your resume and internship data.
            </p>
          </div>
        </div>

        <div className="feature">
          <Briefcase />

          <div>
            <h3>Relevant Results</h3>
            <p>
              Get internships ranked according to your profile.
            </p>
          </div>
        </div>

      </section>

      {/* Results */}
      <section className="results-section">

        <div className="section-heading">

          <span className="small-label">
            AI MATCH RESULTS
          </span>

          <h2>
            Recommended Internships
          </h2>

          <p>
            {results.length > 0
              ? `Found ${results.length} relevant internships for your resume.`
              : "Upload your resume to discover matching internships."}
          </p>

        </div>

        {/* Results Grid */}
        {results.length > 0 && (

          <div className="internship-grid">

            {results.map((internship) => (

              <div
                className="internship-card"
                key={internship.internship_id || internship.rank}
              >

                <div className="card-top">

                  <div className="company-logo">
                    {internship.company
                      ? internship.company.substring(0, 2).toUpperCase()
                      : "AI"}
                  </div>

                  <span className="match-score">
                    {internship.similarity_score}% Match
                  </span>

                </div>

                <h3>
                  {internship.title}
                </h3>

                <p className="company-name">
                  {internship.company}
                </p>

                <div className="details">

                  <span>
                    <MapPin size={16} />
                    {internship.location}
                  </span>

                  <span>
                    <Briefcase size={16} />
                    {internship.work_mode}
                  </span>

                  <span>
                    <Clock size={16} />
                    {internship.duration}
                  </span>

                </div>

                <p className="description">
                  {internship.description}
                </p>

                <div className="skills">

                  {internship.required_skills?.slice(0, 4).map(
                    (skill, index) => (
                      <span key={index}>
                        {skill}
                      </span>
                    )
                  )}

                </div>

                <button
                  className="apply-btn"
                  onClick={() => {
                    alert(`Apply for ${internship.title}`);
                  }}
                >
                  Apply Now
                </button>

              </div>

            ))}

          </div>

        )}

      </section>

    </div>
  );
}

export default App;