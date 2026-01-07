-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 17, 2025 at 05:30 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ai_test_evaluator`
--

-- --------------------------------------------------------

--
-- Table structure for table `activity_logs`
--

CREATE TABLE `activity_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `role` enum('admin','teacher','student') NOT NULL,
  `action` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `activity_logs`
--

INSERT INTO `activity_logs` (`id`, `user_id`, `role`, `action`, `created_at`) VALUES
(1, 1, 'admin', 'Logged in to admin panel', '2025-10-16 18:14:08'),
(2, 2, 'admin', 'Updated settings', '2025-10-16 18:14:08'),
(3, 1, 'teacher', 'Created new exam', '2025-10-16 18:14:08'),
(4, 2, 'teacher', 'Uploaded questions', '2025-10-16 18:14:08'),
(5, 3, 'teacher', 'Checked student reports', '2025-10-16 18:14:08'),
(6, 1, 'student', 'Submitted exam', '2025-10-16 18:14:08'),
(7, 2, 'student', 'Viewed report', '2025-10-16 18:14:08'),
(8, 3, 'student', 'Executed code in editor', '2025-10-16 18:14:08'),
(9, 4, 'student', 'Logged in', '2025-10-16 18:14:08'),
(10, 5, 'student', 'Logged out', '2025-10-16 18:14:08'),
(11, 1, 'student', 'Logged in', '2025-10-16 18:15:29'),
(12, 2, 'student', 'Logged in', '2025-10-16 18:29:17'),
(13, 3, 'student', 'Logged in', '2025-10-16 18:29:58'),
(14, 1, 'teacher', 'Logged in', '2025-10-16 18:36:07'),
(15, 2, 'student', 'Logged in', '2025-10-16 18:36:38'),
(16, 2, 'student', 'Started exam 1', '2025-10-16 18:36:51'),
(17, 2, 'student', 'Submitted exam 1 (AI score 3.9/10)', '2025-10-16 18:38:11'),
(18, 3, 'student', 'Logged in', '2025-10-16 18:39:15'),
(19, 1, 'teacher', 'Logged in', '2025-10-16 18:39:31'),
(20, 3, 'student', 'Logged in', '2025-10-16 18:40:10'),
(21, 3, 'student', 'Started exam 1', '2025-10-16 18:40:22'),
(22, 3, 'student', 'Submitted exam 1 (AI score 4.3/10)', '2025-10-16 18:44:40'),
(23, 3, 'student', 'Submitted exam 1 (AI score 4.3/10)', '2025-10-16 19:10:18'),
(24, 3, 'student', 'Started exam 1', '2025-10-16 19:26:02');

-- --------------------------------------------------------

--
-- Table structure for table `admins`
--

CREATE TABLE `admins` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admins`
--

INSERT INTO `admins` (`id`, `name`, `email`, `password`, `created_at`) VALUES
(1, 'System Admin', 'admin1@example.com', 'admin123', '2025-10-16 18:14:07'),
(2, 'Prashant Kulkarni', 'admin2@example.com', 'admin123', '2025-10-16 18:14:07'),
(3, 'Meena Joshi', 'admin3@example.com', 'admin123', '2025-10-16 18:14:07'),
(4, 'Rohit Patil', 'admin4@example.com', 'admin123', '2025-10-16 18:14:07'),
(5, 'Sneha Jadhav', 'admin5@example.com', 'admin123', '2025-10-16 18:14:07'),
(6, 'Vishal Shinde', 'admin6@example.com', 'admin123', '2025-10-16 18:14:07'),
(7, 'Radha More', 'admin7@example.com', 'admin123', '2025-10-16 18:14:07'),
(8, 'Nilesh Sawant', 'admin8@example.com', 'admin123', '2025-10-16 18:14:07'),
(9, 'Pooja Kadam', 'admin9@example.com', 'admin123', '2025-10-16 18:14:07'),
(10, 'Aniket Deshmukh', 'admin10@example.com', 'admin123', '2025-10-16 18:14:07');

-- --------------------------------------------------------

--
-- Table structure for table `evaluations`
--

CREATE TABLE `evaluations` (
  `id` int(11) NOT NULL,
  `submission_id` int(11) NOT NULL,
  `score` float NOT NULL DEFAULT 0,
  `feedback` text DEFAULT NULL,
  `evaluated_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `evaluations`
--

INSERT INTO `evaluations` (`id`, `submission_id`, `score`, `feedback`, `evaluated_at`) VALUES
(1, 1, 9.5, 'Excellent work, correct output.', '2025-10-16 18:14:08'),
(2, 2, 8, 'Good understanding of OOP.', '2025-10-16 18:14:08'),
(3, 3, 8.5, 'Well structured code.', '2025-10-16 18:14:08'),
(4, 4, 7, 'Correct SQL syntax.', '2025-10-16 18:14:08'),
(5, 5, 7.5, 'Logical implementation correct.', '2025-10-16 18:14:08'),
(6, 6, 7.8, 'Understood complexity concept.', '2025-10-16 18:14:08'),
(7, 7, 7.2, 'Good HTML basics.', '2025-10-16 18:14:08'),
(8, 8, 8.1, 'Good scheduling concept.', '2025-10-16 18:14:08'),
(9, 9, 7.4, 'Networking basics correct.', '2025-10-16 18:14:08'),
(10, 10, 8, 'Good understanding of SDLC.', '2025-10-16 18:14:08'),
(11, 12, 3.9, 'Q1: AI score 7.5/10 (expected like \'Hello World\', saw \'Hello World\')\nQ2: AI score 0.3/10 (expected like \'120\', saw \'Hello World\')', '2025-10-16 18:38:11'),
(12, 14, 4.3, 'Q2: AI score 7.8/10 (expected like \'120\', saw \'120\')\nQ1: AI score 0.9/10 (expected like \'Hello World\', saw \'120\')', '2025-10-16 18:44:40'),
(13, 15, 4.3, 'Q2: AI score 7.8/10 (expected like \'120\', saw \'120\')\nQ1: AI score 0.9/10 (expected like \'Hello World\', saw \'120\')', '2025-10-16 19:10:18');

-- --------------------------------------------------------

--
-- Table structure for table `exams`
--

CREATE TABLE `exams` (
  `id` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text DEFAULT NULL,
  `exam_date` date DEFAULT NULL,
  `duration` int(11) NOT NULL DEFAULT 30,
  `created_by` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `exams`
--

INSERT INTO `exams` (`id`, `title`, `description`, `exam_date`, `duration`, `created_by`, `created_at`) VALUES
(1, 'Python Basics', 'Covers variables, loops, functions', '2025-10-16', 45, 1, '2025-10-16 18:14:08'),
(2, 'C++ Programming', 'Covers OOP, classes, constructors', '2025-10-16', 45, 2, '2025-10-16 18:14:08'),
(3, 'Java Programming', 'Covers core Java, exceptions, arrays', '2025-10-16', 50, 3, '2025-10-16 18:14:08'),
(4, 'Database Concepts', 'Covers SQL, joins, normalization', '2025-10-16', 40, 4, '2025-10-16 18:14:08'),
(5, 'Data Structures', 'Covers arrays, stacks, queues, linked lists', '2025-10-16', 60, 5, '2025-10-16 18:14:08'),
(6, 'Algorithms', 'Sorting, searching, complexity analysis', '2025-10-16', 55, 6, '2025-10-16 18:14:08'),
(7, 'Web Development', 'HTML, CSS, JS, HTTP basics', '2025-10-16', 35, 7, '2025-10-16 18:14:08'),
(8, 'Operating Systems', 'Processes, threads, scheduling', '2025-10-16', 50, 8, '2025-10-16 18:14:08'),
(9, 'Computer Networks', 'OSI model, protocols, routing', '2025-10-16', 40, 9, '2025-10-16 18:14:08'),
(10, 'Software Engineering', 'SDLC, models, testing concepts', '2025-10-16', 45, 10, '2025-10-16 18:14:08');

-- --------------------------------------------------------

--
-- Table structure for table `exam_assignments`
--

CREATE TABLE `exam_assignments` (
  `id` int(11) NOT NULL,
  `exam_id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `assigned_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `exam_assignments`
--

INSERT INTO `exam_assignments` (`id`, `exam_id`, `student_id`, `assigned_at`) VALUES
(2, 2, 2, '2025-10-16 18:14:08'),
(3, 3, 3, '2025-10-16 18:14:08'),
(4, 4, 4, '2025-10-16 18:14:08'),
(5, 5, 5, '2025-10-16 18:14:08'),
(6, 6, 6, '2025-10-16 18:14:08'),
(7, 7, 7, '2025-10-16 18:14:08'),
(8, 8, 8, '2025-10-16 18:14:08'),
(9, 9, 9, '2025-10-16 18:14:08'),
(10, 10, 10, '2025-10-16 18:14:08'),
(13, 1, 10, '2025-10-16 18:39:51'),
(14, 1, 9, '2025-10-16 18:39:51'),
(15, 1, 8, '2025-10-16 18:39:51'),
(16, 1, 7, '2025-10-16 18:39:51'),
(17, 1, 6, '2025-10-16 18:39:51'),
(18, 1, 5, '2025-10-16 18:39:51'),
(19, 1, 4, '2025-10-16 18:39:51'),
(20, 1, 3, '2025-10-16 18:39:51'),
(21, 1, 2, '2025-10-16 18:39:51'),
(22, 1, 1, '2025-10-16 18:39:51');

-- --------------------------------------------------------

--
-- Table structure for table `questions`
--

CREATE TABLE `questions` (
  `id` int(11) NOT NULL,
  `exam_id` int(11) NOT NULL,
  `text` text NOT NULL,
  `correct_output` text DEFAULT NULL,
  `marks` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `questions`
--

INSERT INTO `questions` (`id`, `exam_id`, `text`, `correct_output`, `marks`, `created_at`) VALUES
(1, 1, 'Print \"Hello World\" in Python.', 'Hello World', 2, '2025-10-16 18:14:08'),
(2, 1, 'Write factorial program for n=5', '120', 8, '2025-10-16 18:14:08'),
(3, 2, 'Define a class and create an object.', 'OK', 5, '2025-10-16 18:14:08'),
(4, 3, 'Check if number 7 is prime.', 'true', 5, '2025-10-16 18:14:08'),
(5, 4, 'SQL query to get students with marks > 50', 'RESULT', 4, '2025-10-16 18:14:08'),
(6, 5, 'Reverse the given array [1,2,3]', '3 2 1', 3, '2025-10-16 18:14:08'),
(7, 6, 'What is time complexity of binary search?', 'O(log n)', 2, '2025-10-16 18:14:08'),
(8, 7, 'What type of protocol is HTTP?', 'Stateless', 2, '2025-10-16 18:14:08'),
(9, 8, 'Describe Round Robin scheduling feature.', 'Time Quantum', 3, '2025-10-16 18:14:08'),
(10, 9, 'Which layer is Transport layer in OSI?', 'Layer 4', 3, '2025-10-16 18:14:08');

-- --------------------------------------------------------

--
-- Table structure for table `students`
--

CREATE TABLE `students` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `students`
--

INSERT INTO `students` (`id`, `name`, `email`, `password`, `created_at`) VALUES
(1, 'Ganesh Patil', 'student1@example.com', 'student123', '2025-10-16 18:14:08'),
(2, 'Aarti Deshmukh', 'student2@example.com', 'student123', '2025-10-16 18:14:08'),
(3, 'Ramesh Jadhav', 'student3@example.com', 'student123', '2025-10-16 18:14:08'),
(4, 'Prachi Shinde', 'student4@example.com', 'student123', '2025-10-16 18:14:08'),
(5, 'Saurabh Pawar', 'student5@example.com', 'student123', '2025-10-16 18:14:08'),
(6, 'Kiran Patil', 'student6@example.com', 'student123', '2025-10-16 18:14:08'),
(7, 'Janhavi More', 'student7@example.com', 'student123', '2025-10-16 18:14:08'),
(8, 'Siddharth Joshi', 'student8@example.com', 'student123', '2025-10-16 18:14:08'),
(9, 'Neha Sawant', 'student9@example.com', 'student123', '2025-10-16 18:14:08'),
(10, 'Rohan Deshmukh', 'student10@example.com', 'student123', '2025-10-16 18:14:08');

-- --------------------------------------------------------

--
-- Table structure for table `submissions`
--

CREATE TABLE `submissions` (
  `id` int(11) NOT NULL,
  `exam_id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `status` varchar(32) NOT NULL DEFAULT 'submitted',
  `code` mediumtext DEFAULT NULL,
  `questions_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`questions_json`)),
  `submitted_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `submissions`
--

INSERT INTO `submissions` (`id`, `exam_id`, `student_id`, `status`, `code`, `questions_json`, `submitted_at`, `created_at`) VALUES
(1, 1, 1, 'submitted', 'print(\"Hello World\")', NULL, '2025-10-16 18:14:08', '2025-10-16 18:14:08'),
(2, 2, 2, 'submitted', 'int main(){return 0;}', NULL, '2025-10-16 18:14:08', '2025-10-16 18:14:08'),
(3, 3, 3, 'submitted', 'class Main{public static void main(String[] args){System.out.println(7);}}', NULL, '2025-10-16 18:14:08', '2025-10-16 18:14:08'),
(4, 4, 4, 'submitted', 'SELECT * FROM students;', NULL, '2025-10-16 18:14:08', '2025-10-16 18:14:08'),
(5, 5, 5, 'submitted', '# reverse array', NULL, '2025-10-16 18:14:08', '2025-10-16 18:14:08'),
(6, 6, 6, 'submitted', '// binary search', NULL, '2025-10-16 18:14:08', '2025-10-16 18:14:08'),
(7, 7, 7, 'submitted', '// http notes', NULL, '2025-10-16 18:14:08', '2025-10-16 18:14:08'),
(8, 8, 8, 'submitted', '// rr scheduling', NULL, '2025-10-16 18:14:08', '2025-10-16 18:14:08'),
(9, 9, 9, 'submitted', '// transport layer', NULL, '2025-10-16 18:14:08', '2025-10-16 18:14:08'),
(10, 10, 10, 'submitted', '// SDLC', NULL, '2025-10-16 18:14:08', '2025-10-16 18:14:08'),
(11, 1, 2, 'started', NULL, '[1, 2]', '2025-10-16 18:36:51', '2025-10-16 18:36:51'),
(12, 1, 2, 'submitted', 'print(\"Hello World\")', '[1, 2]', '2025-10-16 18:38:09', '2025-10-16 18:38:09'),
(13, 1, 3, 'started', NULL, '[2, 1]', '2025-10-16 18:40:22', '2025-10-16 18:40:22'),
(14, 1, 3, 'submitted', 'a = 5\r\ni = 1\r\nfact =1 \r\n\r\nwhile(a>0):\r\n   fact*=a\r\n   a-=1\r\n\r\nprint(fact)', '[2, 1]', '2025-10-16 18:44:38', '2025-10-16 18:44:38'),
(15, 1, 3, 'submitted', 'a = 5\r\ni = 1\r\nfact =1 \r\n\r\nwhile(a>0):\r\n   fact*=a\r\n   a-=1\r\n\r\nprint(fact)', '[2, 1]', '2025-10-16 19:10:16', '2025-10-16 19:10:16'),
(16, 1, 3, 'started', NULL, '[1, 2]', '2025-10-16 19:26:02', '2025-10-16 19:26:02');

-- --------------------------------------------------------

--
-- Table structure for table `teachers`
--

CREATE TABLE `teachers` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `teachers`
--

INSERT INTO `teachers` (`id`, `name`, `email`, `password`, `created_at`) VALUES
(1, 'Amol Pawar', 'teacher1@example.com', 'teacher123', '2025-10-16 18:14:07'),
(2, 'Vaishali Joshi', 'teacher2@example.com', 'teacher123', '2025-10-16 18:14:07'),
(3, 'Sandeep More', 'teacher3@example.com', 'teacher123', '2025-10-16 18:14:07'),
(4, 'Kavita Bhosale', 'teacher4@example.com', 'teacher123', '2025-10-16 18:14:07'),
(5, 'Nilesh Sawant', 'teacher5@example.com', 'teacher123', '2025-10-16 18:14:07'),
(6, 'Priya Deshmukh', 'teacher6@example.com', 'teacher123', '2025-10-16 18:14:07'),
(7, 'Sachin Kamble', 'teacher7@example.com', 'teacher123', '2025-10-16 18:14:07'),
(8, 'Geeta Shirsat', 'teacher8@example.com', 'teacher123', '2025-10-16 18:14:07'),
(9, 'Shubhada Patil', 'teacher9@example.com', 'teacher123', '2025-10-16 18:14:07'),
(10, 'Rahul Khot', 'teacher10@example.com', 'teacher123', '2025-10-16 18:14:07');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `activity_logs`
--
ALTER TABLE `activity_logs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `admins`
--
ALTER TABLE `admins`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `evaluations`
--
ALTER TABLE `evaluations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `submission_id` (`submission_id`);

--
-- Indexes for table `exams`
--
ALTER TABLE `exams`
  ADD PRIMARY KEY (`id`),
  ADD KEY `created_by` (`created_by`);

--
-- Indexes for table `exam_assignments`
--
ALTER TABLE `exam_assignments`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_exam_student` (`exam_id`,`student_id`),
  ADD KEY `student_id` (`student_id`);

--
-- Indexes for table `questions`
--
ALTER TABLE `questions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `exam_id` (`exam_id`);

--
-- Indexes for table `students`
--
ALTER TABLE `students`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `submissions`
--
ALTER TABLE `submissions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `exam_id` (`exam_id`),
  ADD KEY `student_id` (`student_id`);

--
-- Indexes for table `teachers`
--
ALTER TABLE `teachers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `activity_logs`
--
ALTER TABLE `activity_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT for table `admins`
--
ALTER TABLE `admins`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `evaluations`
--
ALTER TABLE `evaluations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `exams`
--
ALTER TABLE `exams`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `exam_assignments`
--
ALTER TABLE `exam_assignments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `questions`
--
ALTER TABLE `questions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `students`
--
ALTER TABLE `students`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `submissions`
--
ALTER TABLE `submissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `teachers`
--
ALTER TABLE `teachers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `evaluations`
--
ALTER TABLE `evaluations`
  ADD CONSTRAINT `evaluations_ibfk_1` FOREIGN KEY (`submission_id`) REFERENCES `submissions` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `exams`
--
ALTER TABLE `exams`
  ADD CONSTRAINT `exams_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `teachers` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `exam_assignments`
--
ALTER TABLE `exam_assignments`
  ADD CONSTRAINT `exam_assignments_ibfk_1` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `exam_assignments_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `questions`
--
ALTER TABLE `questions`
  ADD CONSTRAINT `questions_ibfk_1` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `submissions`
--
ALTER TABLE `submissions`
  ADD CONSTRAINT `submissions_ibfk_1` FOREIGN KEY (`exam_id`) REFERENCES `exams` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `submissions_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
