import { KeywordUsage } from "@/types/keywords";
import KeywordBarChart from "./keyword-bar-chart";

export default function KeywordAnalysis({
  mostUsedUserKeywords,
  mostUsedExternalKeywords,
}: {
  mostUsedUserKeywords: KeywordUsage[];
  mostUsedExternalKeywords: KeywordUsage[];
}) {
  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
      <KeywordBarChart
        title="Top 5 Most Used User Defined Keywords"
        keywords={mostUsedUserKeywords}
        barClassName="bg-chart-2"
      />
      <KeywordBarChart
        title="Top 5 Most Used External/BuiltIn Keywords"
        keywords={mostUsedExternalKeywords}
        barClassName="bg-chart-4"
      />
    </div>
  );
}
