import Link from "next/link";


export default function Navbar(){

  return (

    <nav>

      <Link href="/">
        Home
      </Link>


      <Link href="/upload">
        Upload
      </Link>


      <Link href="/dashboard">
        Dashboard
      </Link>


      <Link href="/query">
        Ask AI
      </Link>


    </nav>

  );

}