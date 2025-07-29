# {
#   "quiz_id": 5,
#   "answers": [
#     {
#       "question_id": 5,
#       "selected_option": "framework"
#     },
#     {
#       "question_id": 6,
#       "selected_option": "react hooks"
#     },
#     {
#       "question_id": 7,
#       "selected_option": "no"
#     }
#   ]
# }



# {
#   "quiz_id": 9,
#   "answers": [
#     {
#       "question_id": 11,
#       "selected_option": "to deliver msg"
#     },
#     {
#       "question_id": 12,
#       "selected_option": "nota"
#     }
#   ]
# }


# async def handle_module_status(user_id: int, quiz_id: int, is_passed: bool, db: AsyncSession):
#     """
#     Ensures a record always exists in StudentModuleStatus:
#     - Creates new record if doesn't exist
#     - Updates existing record
#     - Sets both fields based on pass/fail
#     """
#     # 1. Get the quiz's module
#     quiz = await db.scalar(
#         select(Quiz)
#         .where(Quiz.id == quiz_id)
#         .options(selectinload(Quiz.module))
#     )
    
#     if not quiz or not quiz.module:
#         raise HTTPException(404, "Quiz/module not found")

#     # 2. Check if record exists
#     existing_status = await db.scalar(
#         select(StudentModuleStatus)
#         .where(StudentModuleStatus.student_id == user_id)
#         .where(StudentModuleStatus.module_id == quiz.module_id))
    
#     print(f"Existing status for user {user_id} in module {quiz.module_id}: {existing_status}")
#     # 3. Prepare update values
#     update_values = {
#         "is_unlocked": is_passed,
#         "is_completed": is_passed
#     }
#     breakpoint()
#     # 4. Create or update record
#     if existing_status:
#         print(existing_status.id, "exists, updating...###########")
#         # Update existing
#         await db.execute(
#             update(StudentModuleStatus)
#             .where(StudentModuleStatus.id == existing_status.id)
#             .values(**update_values)
#         )
#     else:
#         # Create new
#         db.add(StudentModuleStatus(
#             student_id=user_id,
#             module_id=quiz.module_id,
#             **update_values
#         ))
    
#     await db.commit()