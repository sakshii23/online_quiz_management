 # -------------------- Quiz Attempt --------------------

# class StudentQuizAttempt(Base):
#     __tablename__ = "quiz_attempts"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
#     quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"))
#     submitted_at = Column(DateTime(timezone=True), server_default=func.now())
#     total_marks = Column(Integer)
#     obtained_marks = Column(Integer)
#     is_passed = Column(Boolean, default=False)
#     pdf_path = Column(String, nullable=True)

#     user = relationship("User", back_populates="quiz_attempts")
#     quiz = relationship("Quiz", back_populates="attempts")
#     answers = relationship("QuizAnswer", back_populates="attempt", cascade="all, delete")

# # -------------------- Quiz Answer --------------------

# class QuizAnswer(Base):
#     __tablename__ = "quiz_answers"

#     id = Column(Integer, primary_key=True, index=True)
#     attempt_id = Column(Integer, ForeignKey("quiz_attempts.id", ondelete="CASCADE"))
#     question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))
#     selected_option = Column(String)
#     is_correct = Column(Boolean, default=False)

#     attempt = relationship("StudentQuizAttempt", back_populates="answers")


# class StudentModuleStatus(Base):
#     __tablename__ = "student_module_status"

#     id = Column(Integer, primary_key=True, index=True)
#     student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"))
#     module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"))
#     is_unlocked = Column(Boolean, default=False)
#     is_completed = Column(Boolean, default=False)
#     unlocked_on = Column(DateTime(timezone=True), server_default=func.now())