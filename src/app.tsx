import { MetaProvider, Title } from "@solidjs/meta";
import { Router } from "@solidjs/router";
import { FileRoutes } from "@solidjs/start/router";
import { Suspense } from "solid-js";
import { PortfolioProvider } from "./stores/content";
import { Skeleton } from "./components/atoms/Skeleton";
import "./app.css";

function GlobalSkeleton() {
  return (
    <div class="min-h-screen bg-[#111111] flex flex-col">
      {/* Navbar Skeleton */}
      <header class="sticky top-0 z-50 bg-[#111111]/80 backdrop-blur-md border-b border-zinc-800/50">
        <div class="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <div class="flex items-center gap-1">
            <span class="text-zinc-100 font-semibold">fabio</span>
            <span class="text-zinc-500">.dev</span>
          </div>
          <nav class="flex items-center gap-6">
            <div class="hidden sm:flex items-center gap-6 text-sm text-zinc-400">
              <span>Home</span>
              <span>About</span>
              <span>Blog</span>
              <span>Projects</span>
              <span>Contact</span>
            </div>
            <div class="flex items-center gap-3 text-zinc-500">
              <Skeleton class="w-8 h-8 rounded" />
              <Skeleton class="w-8 h-8 rounded" />
              <Skeleton class="w-8 h-8 rounded" />
            </div>
          </nav>
        </div>
      </header>

      {/* Main Content Skeleton */}
      <main class="flex-1 max-w-3xl mx-auto w-full px-4 py-12">
        {/* Hero Section */}
        <div class="bg-zinc-900/30 rounded-2xl p-8 mb-10">
          <div class="flex flex-col md:flex-row gap-8 items-start">
            <Skeleton class="w-24 h-24 sm:w-28 sm:h-28 rounded-full shrink-0" />
            <div class="flex-1 space-y-3 w-full">
              <Skeleton class="h-7 w-3/4" />
              <Skeleton class="h-4 w-1/3" />
              <Skeleton class="h-4 w-full" />
              <Skeleton class="h-4 w-4/5" />
              <div class="flex gap-3 pt-2">
                <Skeleton class="h-9 w-20 rounded-lg" />
                <Skeleton class="h-9 w-20 rounded-lg" />
                <Skeleton class="h-9 w-16 rounded-lg" />
              </div>
            </div>
          </div>
        </div>

        {/* Latest Blog Section */}
        <section class="mb-10">
          <Skeleton class="h-3 w-32 mb-4" />
          <div class="space-y-4">
            <Skeleton class="h-20 w-full rounded-xl" />
            <Skeleton class="h-20 w-full rounded-xl" />
          </div>
        </section>

        {/* Projects Section */}
        <section class="mb-10">
          <Skeleton class="h-3 w-36 mb-4" />
          <Skeleton class="h-20 w-full rounded-xl" />
        </section>

        {/* Contact Section */}
        <section>
          <Skeleton class="h-24 w-full rounded-xl" />
        </section>
      </main>

      {/* Footer Skeleton */}
      <footer class="border-t border-zinc-800/50 py-6">
        <div class="max-w-3xl mx-auto px-4 flex items-center justify-between">
          <span class="text-sm text-zinc-500">© 2025 Fabio Souza.</span>
          <div class="flex items-center gap-4">
            <Skeleton class="w-5 h-5 rounded" />
            <Skeleton class="w-5 h-5 rounded" />
            <Skeleton class="w-5 h-5 rounded" />
            <Skeleton class="w-5 h-5 rounded" />
            <Skeleton class="w-5 h-5 rounded" />
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <Router
      root={props => (
        <MetaProvider>
          <Title>Fabio Souza - Portfolio</Title>
          <PortfolioProvider>
            <Suspense fallback={<GlobalSkeleton />}>{props.children}</Suspense>
          </PortfolioProvider>
        </MetaProvider>
      )}
    >
      <FileRoutes />
    </Router>
  );
}
