import Link from "next/link";

export function Logo() {
  return (
    <Link className="brand" href="/" aria-label="EdgeBoard home">
      <span className="brandMark">E</span>
      <span>
        <b>EdgeBoard</b>
        <small>SPORTS INTELLIGENCE</small>
      </span>
    </Link>
  );
}
