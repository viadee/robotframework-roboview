import { BarChart2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { KeywordUsage } from "@/types/keywords";

export default function KeywordBarChart({
  title,
  keywords,
  barClassName,
}: {
  title: string;
  keywords: KeywordUsage[];
  barClassName: string;
}) {
  const maxUsage = Math.max(
    ...keywords.map((keyword) => keyword.total_usages),
    1,
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {keywords.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-2 py-8 text-muted-foreground">
            <BarChart2 className="w-8 h-8 opacity-40" />
            <p className="text-sm">No data available</p>
          </div>
        ) : (
          <div className="space-y-3">
            {keywords.map((keyword, index) => {
              const percentage = (keyword.total_usages / maxUsage) * 100;
              return (
                <div key={keyword.keyword_id || index} className="space-y-1.5">
                  <div className="flex items-center justify-between gap-2">
                    <div
                      className="truncate text-sm"
                      title={keyword.keyword_name_with_prefix}
                    >
                      {keyword.keyword_name_without_prefix}
                    </div>
                    <Badge variant="outline">{keyword.total_usages}</Badge>
                  </div>
                  <div className="bg-muted h-2 w-full overflow-hidden rounded-full">
                    <div
                      className={`h-full rounded-full ${barClassName}`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
