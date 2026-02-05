import React from "react";

interface ProjectInfoProps {
  projectPath: string;
}

const ProjectInfo: React.FC<ProjectInfoProps> = ({ projectPath }) => {
  const getProjectName = (path: string): string => {
    if (!path) return "No project loaded";
    const parts = path.split("/");
    return parts[parts.length - 1] || "Robot Framework Project";
  };

  return (
    <div className="project-info">
      <div className="project-name">{getProjectName(projectPath)}</div>
      <div className="project-path">
        {projectPath || "No project path available"}
      </div>
    </div>
  );
};

export default ProjectInfo;
