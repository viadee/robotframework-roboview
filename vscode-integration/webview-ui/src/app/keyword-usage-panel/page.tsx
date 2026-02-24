import { useEffect, useMemo, useState } from "react";
import { AppLayout } from "@/components/layout/layout";
import { SidebarKeywordUsage } from "@/app/keyword-usage-panel/sidebar-kw";
import { MainContentKeywordUsage } from "./main-content-kw";
import { DetailsPanelKeywordUsage } from "./details-panel-kw";
import { useMessageListener } from "@/hooks/useMessageListener";
import { FileSelect } from "@/types/files";
import {
  FileUsage,
  FilterItem,
  Keyword,
  KeywordSimilarity,
} from "@/types/keywords";
import { deduplicateKeywords } from "@/utilities/keyword_utils";
import { vscode } from "@/utilities/vscode";

export default function KeywordUsagePage() {
  const [allFiles, setAllFiles] = useState<FileSelect[]>([]);
  const [selectedResource, setSelectedResource] = useState<FileSelect | null>(
    null,
  );
  const [fileSelected, setFileSelected] = useState(false);
  const [currentFilter, setCurrentFilter] = useState("all");

  const [initKeywords, setInitKeywords] = useState<Keyword[]>([]);
  const [calledKeywords, setCalledKeywords] = useState<Keyword[]>([]);
  const [keywordsWithoutDoc, setKeywordsWithoutDoc] = useState<Keyword[]>([]);
  const [keywordsWithoutUsages, setKeywordsWithoutUsages] = useState<Keyword[]>(
    [],
  );
  const [keywordDuplicates, setKeywordDuplicates] = useState<Keyword[]>([]);
  const [selectedKeyword, setSelectedKeyword] = useState<Keyword | null>(null);
  const [robotFileUsages, setRobotFileUsages] = useState<FileUsage[]>([]);
  const [resourceFileUsages, setResourceFileUsages] = useState<FileUsage[]>([]);
  const [keywordSimilarity, setKeywordSimilarity] = useState<
    KeywordSimilarity[]
  >([]);
  const [keywordSimilaritySources, setKeywordSimilaritySources] = useState<
    Record<string, string>
  >({});

  useMessageListener({
    allFiles: (message) => {
      setAllFiles(message.files || []);
    },
    initKeywords: (message) => {
      setInitKeywords(message.init_keywords || []);
    },
    calledKeywords: (message) => {
      setCalledKeywords(message.called_keywords || []);
    },
    keywordsWithoutDoc: (message) => {
      setKeywordsWithoutDoc(message.keywords || []);
    },
    keywordsWithoutUsages: (message) => {
      setKeywordsWithoutUsages(message.keywords || []);
    },
    keywordDuplicates: (message) => {
      setKeywordDuplicates(message.keywords || []);
    },
    keywordUsageRobot: (message) => {
      setRobotFileUsages(message.usage || []);
    },
    keywordUsageResource: (message) => {
      setResourceFileUsages(message.usage || []);
    },
    keywordSimilarity: (message) => {
      const similarityList = message.similarity || [];
      const sources: Record<string, string> = {};

      similarityList.forEach((keyword: KeywordSimilarity) => {
        if (keyword.source) {
          sources[keyword.keyword_name_without_prefix] = keyword.source;
        }
      });

      setKeywordSimilarity(similarityList);
      setKeywordSimilaritySources(sources);
    },
  });

  useEffect(() => {
    vscode.postMessage({ command: "getAllFiles" });
    vscode.postMessage({ command: "getKeywordsWithoutDoc" });
    vscode.postMessage({ command: "getKeywordsWithoutUsages" });
    vscode.postMessage({ command: "getKeywordDuplicates" });
  }, []);

  useEffect(() => {
    if (!selectedResource) {
      setInitKeywords([]);
      setCalledKeywords([]);
      setSelectedKeyword(null);
      setRobotFileUsages([]);
      setResourceFileUsages([]);
      setKeywordSimilarity([]);
      setKeywordSimilaritySources({});
      return;
    }

    vscode.postMessage({
      command: "getInitKeywords",
      filePath: selectedResource.path,
    });
    vscode.postMessage({
      command: "getCalledKeywords",
      filePath: selectedResource.path,
    });
  }, [selectedResource]);

  const typeFilters = useMemo<FilterItem[]>(() => {
    const allKeywords = deduplicateKeywords([
      ...initKeywords,
      ...calledKeywords,
    ]);

    return [
      { id: "all", label: "All Keywords", count: allKeywords.length },
      {
        id: "initialized",
        label: "Initialized Keywords",
        count: deduplicateKeywords(initKeywords).length,
      },
      {
        id: "called",
        label: "Called Keywords",
        count: deduplicateKeywords(calledKeywords).length,
      },
    ];
  }, [calledKeywords, initKeywords]);

  const globalFilters = useMemo<FilterItem[]>(() => {
    return [
      {
        id: "kw_wo_doc",
        label: "Keywords without Documentation",
        count: deduplicateKeywords(keywordsWithoutDoc).length,
      },
      {
        id: "kw_wo_usages",
        label: "Unused Keywords",
        count: deduplicateKeywords(keywordsWithoutUsages).length,
      },
      {
        id: "kw_duplicates",
        label: "Potential Duplicate Keywords",
        count: deduplicateKeywords(keywordDuplicates).length,
      },
    ];
  }, [keywordDuplicates, keywordsWithoutDoc, keywordsWithoutUsages]);

  const handleResourceChange = (resource: FileSelect | null) => {
    setSelectedResource(resource);
    setFileSelected(resource !== null);
    setSelectedKeyword(null);
    setRobotFileUsages([]);
    setResourceFileUsages([]);
    setKeywordSimilarity([]);
    setKeywordSimilaritySources({});

    if (!resource) {
      setCurrentFilter("all");
    }
  };

  const handleKeywordSelect = (keyword: Keyword) => {
    setSelectedKeyword(keyword);

    vscode.postMessage({
      command: "getKeywordUsageRobot",
      keyword: keyword.keyword_name_with_prefix,
    });
    vscode.postMessage({
      command: "getKeywordUsageResource",
      keyword: keyword.keyword_name_with_prefix,
    });
    vscode.postMessage({
      command: "getKeywordSimilarity",
      keyword: keyword.keyword_name_with_prefix,
    });
  };

  return (
    <AppLayout
      sidebar={
        <SidebarKeywordUsage
          allFiles={allFiles}
          selectedFilePath={selectedResource?.path ?? null}
          onFileChange={handleResourceChange}
          typeFilters={typeFilters}
          globalFilters={globalFilters}
          currentFilter={currentFilter}
          onFilterChange={setCurrentFilter}
        />
      }
      content={
        <MainContentKeywordUsage
          initKeywords={initKeywords}
          calledKeywords={calledKeywords}
          keywordsWithoutDoc={keywordsWithoutDoc}
          keywordsWithoutUsages={keywordsWithoutUsages}
          keywordDuplicates={keywordDuplicates}
          currentFilter={currentFilter}
          fileSelected={fileSelected}
          selectedKeywordId={selectedKeyword?.keyword_id ?? null}
          onKeywordSelect={handleKeywordSelect}
        />
      }
      details={
        <DetailsPanelKeywordUsage
          selectedKeyword={selectedKeyword}
          robotFileUsages={robotFileUsages}
          resourceFileUsages={resourceFileUsages}
          keywordSimilarity={keywordSimilarity}
          keywordSimilaritySources={keywordSimilaritySources}
        />
      }
    />
  );
}
