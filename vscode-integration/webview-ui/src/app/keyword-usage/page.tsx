import React, { useState, useEffect, useCallback } from "react";
import { vscode } from "../../utilities/vscode";
import { useMessageListener } from "../../hooks/useMessageListener";
import { Keyword, KeywordSimilarity, FilterItem } from "../../types/keywords";
import { FileSelect } from "../../types/files";
import { FileUsage } from "../../types/files";
import { deduplicateKeywords } from "../../utilities/keyword_utils";
import Layout from "../../components/layout/layout";
import DetailsPanelKeywordUsage from "../../components/keyword-usage/details-panel-kw";
import KeywordSidebar from "../../components/keyword-usage/sidebar-kw";
import MainContentKeywordUsage from "../../components/keyword-usage/main-content-kw";

const KeywordUsageView: React.FC = () => {
  // State
  const [all_files, setAllFiles] = useState<FileSelect[]>([]);
  const [selectedResource, setSelectedResource] = useState<FileSelect | null>(
    null,
  );

  const [initKeywords, setInitKeywords] = useState<Keyword[]>([]);
  const [calledKeywords, setCalledKeywords] = useState<Keyword[]>([]);
  const [keywordsWithoutDoc, setKeywordsWithoutDoc] = useState<Keyword[]>([]);
  const [keywordsWithoutUsages, setKeywordsWithoutUsages] = useState<Keyword[]>(
    [],
  );
  const [keywordDuplicates, setKeywordDuplicates] = useState<Keyword[]>([]);
  const [selectedKeyword, setSelectedKeyword] = useState<Keyword | null>(null);

  const [currentFilter, setCurrentFilter] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("sort");

  const [robotFileUsages, setRobotFileUsages] = useState<FileUsage[]>([]);
  const [resourceFileUsages, setResourceFileUsages] = useState<FileUsage[]>([]);
  const [keywordSimilarity, setKeywordSimilarity] = useState<
    KeywordSimilarity[]
  >([]);
  const [keywordSimilaritySources, setKeywordSimilaritySources] = useState<
    Record<string, string>
  >({});
  const [fileSelected, setFileSelected] = useState(false);

  useMessageListener({
    allFiles: (message) => {
      const files = message.files || [];
      setAllFiles(
        files.map((file: FileSelect) => ({
          file_name: file.file_name,
          path: file.path,
        })),
      );
    },
    initKeywords: (message) => {
      const keywords = message.init_keywords || [];
      setInitKeywords(
        keywords.map((kw: Keyword) => ({
          keyword_id: kw.keyword_id,
          file_name: kw.file_name,
          keyword_name_without_prefix: kw.keyword_name_without_prefix,
          keyword_name_with_prefix: kw.keyword_name_with_prefix,
          documentation: kw.documentation,
          source: kw.source,
          file_usages: kw.file_usages,
          total_usages: kw.total_usages,
        })),
      );
    },
    calledKeywords: (message) => {
      const keywords = message.called_keywords || [];
      setCalledKeywords(
        keywords.map((kw: Keyword) => ({
          keyword_id: kw.keyword_id,
          file_name: kw.file_name,
          keyword_name_without_prefix: kw.keyword_name_without_prefix,
          keyword_name_with_prefix: kw.keyword_name_with_prefix,
          documentation: kw.documentation,
          source: kw.source,
          file_usages: kw.file_usages,
          total_usages: kw.total_usages,
        })),
      );
    },
    keywordsWithoutDoc: (message) => {
      const keywords = message.keywords || [];
      setKeywordsWithoutDoc(
        keywords.map((kw: Keyword) => ({
          keyword_id: kw.keyword_id,
          file_name: kw.file_name,
          keyword_name_without_prefix: kw.keyword_name_without_prefix,
          keyword_name_with_prefix: kw.keyword_name_with_prefix,
          documentation: kw.documentation,
          source: kw.source,
          file_usages: kw.file_usages,
          total_usages: kw.total_usages,
        })),
      );
    },
    keywordsWithoutUsages: (message) => {
      const keywords = message.keywords || [];
      setKeywordsWithoutUsages(
        keywords.map((kw: Keyword) => ({
          keyword_id: kw.keyword_id,
          file_name: kw.file_name,
          keyword_name_without_prefix: kw.keyword_name_without_prefix,
          keyword_name_with_prefix: kw.keyword_name_with_prefix,
          documentation: kw.documentation,
          source: kw.source,
          file_usages: kw.file_usages,
          total_usages: kw.total_usages,
        })),
      );
    },
    keywordDuplicates: (message) => {
      const keywords = message.keywords || [];
      setKeywordDuplicates(
        keywords.map((kw: Keyword) => ({
          keyword_id: kw.keyword_id,
          file_name: kw.file_name,
          keyword_name_without_prefix: kw.keyword_name_without_prefix,
          keyword_name_with_prefix: kw.keyword_name_with_prefix,
          documentation: kw.documentation,
          source: kw.source,
          file_usages: kw.file_usages,
          total_usages: kw.total_usages,
        })),
      );
    },
    keywordUsageRobot: (message) => {
      const file = message.usage || [];
      setRobotFileUsages(
        file.map((file: FileUsage) => ({
          file_name: file.file_name,
          path: file.path,
          usages: file.usages,
        })),
      );
    },
    keywordUsageResource: (message) => {
      const file = message.usage || [];
      setResourceFileUsages(
        file.map((file: FileUsage) => ({
          file_name: file.file_name,
          path: file.path,
          usages: file.usages,
        })),
      );
    },
    keywordSimilarity: (message) => {
      const similar_kw = message.similarity || [];
      const sources: Record<string, string> = {};

      setKeywordSimilarity(
        similar_kw.map((kw: KeywordSimilarity) => {
          // Sammle die Source-Pfade für spätere Verwendung
          if (kw.source) {
            sources[kw.keyword_name_without_prefix] = kw.source;
          }
          return {
            keyword_id: kw.keyword_id,
            keyword_name_without_prefix: kw.keyword_name_without_prefix,
            keyword_name_with_prefix: kw.keyword_name_with_prefix,
            source: kw.source,
            score: kw.score,
          };
        }),
      );

      setKeywordSimilaritySources(sources);
    },
  });

  useEffect(() => {
    vscode.postMessage({ command: "getAllFiles" });
    vscode.postMessage({ command: "getProjectPath" });
    vscode.postMessage({ command: "getKeywordsWithoutDoc" });
    vscode.postMessage({ command: "getKeywordsWithoutUsages" });
    vscode.postMessage({ command: "getKeywordDuplicates" });
  }, []);

  useEffect(() => {
    if (selectedResource) {
      vscode.postMessage({
        command: "getInitKeywords",
        filePath: selectedResource.path,
      });
      vscode.postMessage({
        command: "getCalledKeywords",
        filePath: selectedResource.path,
      });
    } else {
      setInitKeywords([]);
      setCalledKeywords([]);
    }
  }, [selectedResource]);

  const handleKeywordClick = (keyword: Keyword) => {
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

  const handleClear = () => {
    setSearchTerm("");
  };

  const handleResourceChange = useCallback((resource: FileSelect | null) => {
    setSelectedResource(resource);
    setFileSelected(true);
    if (resource) {
      vscode.postMessage({
        command: "getInitKeywords",
        filePath: resource.path,
      });
      vscode.postMessage({
        command: "getCalledKeywords",
        filePath: resource.path,
      });
    }
  }, []);

  const calculateCountsForTypeFilter = (): FilterItem[] => {
    const allKeywords = [...initKeywords, ...calledKeywords];

    return [
      {
        id: "all",
        label: "All Keywords",
        count: deduplicateKeywords(allKeywords).length,
      },
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
  };

  const calculateCountsForGlobalFilter = (): FilterItem[] => {
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
  };

  const transformedSimilarity =
    keywordSimilarity.length > 0
      ? {
          similar_keywords: keywordSimilarity.reduce(
            (acc, kw) => {
              acc[kw.keyword_name_without_prefix] = kw.score;
              return acc;
            },
            {} as Record<string, number>,
          ),
        }
      : null;

  return (
    <Layout
      sidebar={
        <KeywordSidebar
          selectedResource={selectedResource}
          all_files={all_files}
          handleResourceChange={handleResourceChange}
          calculateCountsForTypeFilter={calculateCountsForTypeFilter}
          calculateCountsForGlobalFilter={calculateCountsForGlobalFilter}
          currentFilter={currentFilter}
          setCurrentFilter={setCurrentFilter}
        />
      }
      mainContent={
        <MainContentKeywordUsage
          initKeywords={initKeywords}
          calledKeywords={calledKeywords}
          keywordsWithoutDoc={keywordsWithoutDoc}
          keywordsWithoutUsages={keywordsWithoutUsages}
          keywordDuplicates={keywordDuplicates}
          currentFilter={currentFilter}
          searchTerm={searchTerm}
          sortBy={sortBy}
          onSortChange={setSortBy}
          onSearchChange={setSearchTerm}
          onClear={handleClear}
          selectedKeyword={selectedKeyword}
          fileSelected={fileSelected}
          onKeywordClick={handleKeywordClick}
        />
      }
      detailsPanel={
        <DetailsPanelKeywordUsage
          selectedKeyword={selectedKeyword}
          testFiles={robotFileUsages}
          resourceFiles={resourceFileUsages}
          keywordSimilarity={transformedSimilarity}
          keywordSimilaritySources={keywordSimilaritySources}
        />
      }
    />
  );
};
export default KeywordUsageView;
