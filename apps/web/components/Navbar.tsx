import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="p-4 bg-gray-800 text-white">
      <ul className="flex space-x-6">
        <li>
          <Link href="/">Home</Link>
        </li>
        <li>
          <Link href="/manager">Manager Interface</Link>
        </li>
        <li>
          <Link href="/documents">Documents</Link>
        </li>
        <li>
          <Link href="/projects">Projects</Link>
        </li>
        <li>
          <Link href="/meetings">meetings</Link>
        </li>
        <li>
          <Link href="/help">Help</Link>
        </li>
      </ul>
    </nav>
  );
}