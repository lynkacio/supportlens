interface PageContainerProps {
  children: React.ReactNode;
}


export default function PageContainer({
  children,
}: PageContainerProps) {

  return (
    <main className="max-w-5xl mx-auto p-8">

      {children}

    </main>
  );

}