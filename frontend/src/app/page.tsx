"use client";
import React, { useState } from "react";
import Head from "next/head";
import Folder from "@/components/FolderIconCard";
import { useRouter } from "next/navigation";
import Breadcrumb from "@/components/ui/Breadcrumb";
import Title from "@/components/ui/Title";
import { Button } from "@/components/ui/Button";
import { Loader2, PlusIcon, GridIcon, ListIcon } from "lucide-react";
import { ProjectData } from "@/interfaces/projects";
import { GetProjects } from "@/services/projects";
import { useQuery } from "@tanstack/react-query";
import Toggle from "@/components/ui/Toggle";
import { Table, Column } from "@/components/ui/Table";
import Pagination from "@/components/ui/Pagination";

export default function Projects() {
  const router = useRouter();
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);

  const { data: response, isLoading } = useQuery({
    queryKey: ["projects", page, pageSize],
    queryFn: () => GetProjects(page, pageSize),
  });

  const projects: ProjectData[] = response?.data?.data || [];
  const totalProjects = response?.data?.total_count || 0;
  const totalPages = Math.ceil(totalProjects / pageSize);

  const handleProjectClick = (id: string) => {
    router.push(`/projects/${id}`);
  };

  const newProject = () => {
    router.push("/projects/new");
  };

  if (!isLoading && projects?.length === 0) {
    newProject();
  }

  const breadcrumbItems = [{ label: "Projects", href: "/" }];

  const viewOptions = [
    { value: "grid", label: "Grid", icon: GridIcon },
    { value: "table", label: "Table", icon: ListIcon },
  ];

  const columns: Column<ProjectData>[] = [
    { header: "Project Name", accessor: "name" },
    { header: "Created At", accessor: "created_at" },
    { header: "Updated At", accessor: "updated_at" },
  ];

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  return (
    <>
      <Head>
        <title>BambooETL - Projects</title>
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <Breadcrumb items={breadcrumbItems} classNames="mb-8" />
      <div className="flex justify-between items-center mb-8">
        <Title margin={false}>My projects</Title>
        <div className="flex space-x-4">
          <Toggle
            options={viewOptions}
            value={viewMode}
            onChange={(value) => setViewMode(value as "grid" | "table")}
          />
          <Button onClick={newProject} icon={PlusIcon}>
            New project
          </Button>
        </div>
      </div>
      {isLoading && <Loader2 className="w-8 h-8 animate-spin" />}
      {projects.length > 0 && (
        <>
          {viewMode === "grid" ? (
            <div className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-2">
              {projects.map((project) => (
                <Folder
                  key={project.id}
                  name={project.name}
                  onClick={() => handleProjectClick(project.id)}
                />
              ))}
            </div>
          ) : (
            <Table
              data={projects}
              columns={columns}
              onRowClick={(project) => handleProjectClick(project.id)}
            />
          )}
          {totalPages > 1 && (
            <Pagination
              currentPage={page}
              totalPages={totalPages}
              onPageChange={handlePageChange}
            />
          )}
        </>
      )}
    </>
  );
}
