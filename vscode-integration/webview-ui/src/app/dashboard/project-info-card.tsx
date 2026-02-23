import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function ProjectInfoCard({
  projectPath,
}: {
  projectPath: string;
}) {
  const getProjectName = (path: string): string => {
    if (!path) return "No project loaded";
    const parts = path.split(/[\\/]/);
    return parts[parts.length - 1] || "Robot Framework Project";
  };

  return (
    <Card>
      <CardHeader className="gap-1">
        <CardTitle className="text-lg">{getProjectName(projectPath)}</CardTitle>
        <CardDescription className="break-all">
          {projectPath || "No project path available"}
        </CardDescription>
      </CardHeader>
    </Card>
  );
}
