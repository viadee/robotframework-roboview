import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { IssueSummary } from "@/types/dashboard";

export default function RobocopIssuesSummary({
  issues,
}: {
  issues: IssueSummary[];
}) {
  const sortedIssues = [...issues].sort((a, b) => b.count - a.count);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Issues by Category</CardTitle>
        <CardDescription>
          Overview of detected Robocop violations grouped by category
        </CardDescription>
      </CardHeader>
      <CardContent>
        {sortedIssues.length === 0 ? (
          <p className="text-muted-foreground text-sm">No issues available</p>
        ) : (
          <div className="space-y-3">
            {sortedIssues.map((issue, index) => (
              <div key={`${issue.category}-${index}`} className="space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-medium">{issue.category}</span>
                  <Badge
                    variant={issue.count > 0 ? "destructive" : "secondary"}
                  >
                    {issue.count}
                  </Badge>
                </div>
                <Separator />
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
